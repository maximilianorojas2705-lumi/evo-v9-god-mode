import argparse
import json
import os
import csv
from datetime import datetime

FIELDNAMES = ['id', 'desc', 'tags', 'time', 'duration', 'authorId', 'authorName', 'authorSignature', 'authorIsVerified', 'url', 
              'authorFollowerCount', 'authorVideoCount', 'soundName', 'diggCount', 'commentCount', 'playCount', 'stickerText']

# initialize parser
parser = argparse.ArgumentParser(description='parse useful data from .har files of network interactions with TikTok')
parser.add_argument('input_file', 
                    help='source file of type .har')
parser.add_argument('-o', '--out', 
                    help='destination file for parsed data')
parser.add_argument('-t', '--type', help='json (default) or csv')

# parse and validate command line arguments
args = parser.parse_args()

if not os.path.exists(args.input_file):
    print('ERROR: invalid path for input file')

if not args.input_file.endswith('.har'):
    print('ERROR: input file must be of type .har')
    exit()

if args.type not in ['json', 'csv', None]:
    print(f'WARNING: unrecognized output type {args.type}, defaulting to json')

# if no output file is given, set default
if not args.out:
    args.out = 'out.' + (args.type or 'json')

# create output file if not exists
if not os.path.exists(args.out):
    with open(args.out, 'w'): pass

# read from input file, write to output file
with open(args.input_file, 'r') as inf, open(args.out, 'w') as outf:
    dicts, log = [], {'parseDateTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), 'browser': {}}

    # read data from .har file
    while line := inf.readline():
        # store browser data
        if line.strip().startswith('"browser"'):
            log['browser']['name'] = inf.readline().split()[1][1:-2]
            log['browser']['name'] = inf.readline().split()[1][1:-1]

        # store date from file if not yet stored
        elif line.strip().startswith('"startedDateTime"') and not 'scrapeDateTime' in log.keys():
            log['scrapeDateTime'] = ':'.join(line.split(':')[1:])[:-2].split('.')[0]

        # load json data for individual tiktoks
        if line.strip().startswith('"content"'):
            if inf.readline().split(':')[1].startswith(' "application/json'):
                inf.readline()
                raw = ':'.join(inf.readline().split(':')[1:])[2:-2] # remove trailing whitespace and quotes
                raw = raw.replace('\\"', '"').replace('\\\\', '\\') # fix escape sequences
                try: # catches malformed json, behavior could be browser-dependent
                    content = json.loads(raw)
                    if content.get('status_code', 0) == 203: # json data for individual tiktoks has this code
                        dicts.append(content)
                except:
                    ...

    # parse data (see README for explanation of each field)
    parsed = []
    for batch in dicts: # data are received in batches of 11-12 tiktoks
        for item in batch['data']:
            if 'item' not in item.keys(): # catches extraneous content from feed
                continue
            info, data = item['item'], {}
            data['id'] = info['id']
            data['desc'] = info['desc']
            data['tags'] = [token[1:] for token in info['desc'].split() if token.startswith('#')]
            data['time'] = datetime.fromtimestamp(info['createTime']).strftime('%Y-%m-%dT%H:%M:%S')
            data['duration'] = info['video']['duration']
            data['author'] = {
                'id': info['author']['uniqueId'],
                'name': info['author']['nickname'],
                'signature': info['author']['signature'],
                'isVerified': info['author']['verified'],
                'followerCount': info['authorStats']['followerCount'],
                'videoCount': info['authorStats']['videoCount']
            }
            data['soundName'] = info['music']['title']
            data['diggCount'] = info['stats']['diggCount']
            data['commentCount'] = info['stats']['commentCount']
            data['playCount'] = info['stats']['playCount']
            
            stickers = []
            for sticker in info.get('stickersOnItem', []):
                for text in sticker.get('stickerText', []):
                    stickers.append(text)
            data['stickerText'] = stickers

            author, video_id = '@' + info['author']['uniqueId'], info['id']
            data['url'] = f'www.tiktok.com/{author}/video/{video_id}'

            parsed.append(data)

    # write parsed data
    if args.type == 'csv':
        flat_parsed = []
        for data in parsed:
            flat_data = {}
            for key in ['id', 'desc', 'time', 'duration', 'soundName', 'diggCount', 'commentCount', 'playCount', 'url']:
                flat_data[key] = data[key]
            flat_data['tags'] = ' '.join(data['tags'])
            flat_data['stickerText'] = ' '.join(data['stickerText'])
            for key, value in data['author'].items():
                flat_data[f'author{key[0].capitalize()}{key[1:]}'] = value
            flat_parsed.append(flat_data)

        writer = csv.DictWriter(outf, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(flat_parsed)
    else:
        outf.write(f'{{\n  "log": {json.dumps(log)},\n')
        outf.write('  "items": [\n    ')
        for i, data in enumerate(parsed):
            outf.write(json.dumps(data, indent=2, ))
            if i != len(parsed) - 1:
                outf.write(',\n    ')
        outf.write('\n  ]\n}\n')
    print(f'Successfully parsed {len(parsed)} TikToks.')

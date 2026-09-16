# Introduction
This repository contains `parse_har.py`, a command-line tool for parsing data from TikTok in the form of `.har` files, a JSON-like format used to track network information.

# Usage
**Note**: these instructions are based on Firefox for Ubuntu 20.04 and have not been tested on other browsers or systems. `parse_har.py` is written for Python 3.9 but should be compatible with any Python 3.0 or later.

1. Open the browser and right-click anywhere in the window. Select 'Inspect', and navigate to the 'Network' tab on the window that appears at the bottom of the browser. If this does not work on your browser, look up how to open your browser's developer tools.
2. Navigate to TikTok and use the search feature to retrieve the tag, user, or topic you are interested in. Scroll down and choose 'Load more' once you reach the bottom of the page (there is no need to select the individual videos) until you have viewed the desired number of TikToks.
3. Click the gear icon in the upper right of the 'Inspect' window and select 'Save All As HAR'. Take note of where you save the file.
4. Download `parse_har.py` from this repository. Next, open a terminal and run the following:
   ```
   python3.9 parse_har.py <path/to/input>
   ```
   This will create a JSON file containing the parsed data in the current directory. For more information on command-line usage, see below under [Command Line Options](#command-line-options).

   **Note**: the command above will only work as given if your Python installation is located at `python3.9` and `parse_har.py` is in the current directory.
5. If all went well, you should see a message like the following:
   ```
   Successfully parsed 390 TikToks into out.csv.
   ```

# Command Line Options
Command line syntax for `parse_har.py` is as follows:
```
parse_har.py <path/to/input> [-o </path/to/output>] [-t json | csv]
```
Both options also have long versions `--out` and `--type`. If no output type is given or the given type is anything other than `json` or `csv`, JSON will be used. If no output file is given, the file will be name `out` with the appropriate extension. 

# Fields
`parse_har.py` scrapes the following fields from network data sent by TikTok.

name | description | type
---- | ----------- | ----
`id` | the internal id used by TikTok to identify unique videos | `int`
`desc` | the video caption | `str`
`tags` | any space-separated tokens in the caption beginning with `'#'`, computed from `desc` | `list[str]`
`time` | the date and time the video was posted | `str`
`duration` | the length, in seconds, of the video | `int`
`authorId` | the unique identifier of the video creator | `str`
`authorName` | the display name of the video creator | `str`
`authorSignature` | the short bio that appears on the creator's account page | `str`
`authorIsVerified` | whether the author's account is verified | `bool`
`url` | a direct link to the video, computed from `authorId` and `id` | `str`
`authorFollowerCount` | the number of followers the creator has | `int`
`authorVideoCount` | the number of videos the creator has | `int`
`soundName` | the name of the sound used in the video | `str`
`diggCount` | the number of diggs the video has (users will know this as the number next to the heart symbol) | `int`
`commentCount` | the number of comments on the video | `int`
`playCount` | the number of times the video has been played | `int`
`stickerText` | text that appears on screen, if it has been added in the TikTok creator interface | `list[str]`

**Note**: With CSV output, any fields of type `list[str]` will instead be a single space-separated string.

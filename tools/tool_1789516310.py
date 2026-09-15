import random

def generate_amazon_affiliate_video_ideas(n=10):
    categories = [
        "review de gadgets", "comparativa de productos", "tutorial de uso", 
        "top 5 de la semana", "unboxing sorpresa", "cómo ahorrar", 
        "mejores ofertas", "análisis de rendimiento", "guía de compra", 
        "preguntas frecuentes"
    ]
    product_types = [
        "smartphones", "televisores", "cámaras", "libros", "ropa deportiva",
        "cocina", "juguetes", "muebles", "accesorios de viaje", "cuidado personal"
    ]
    ideas = []
    for _ in range(n):
        cat = random.choice(categories)
        prod = random.choice(product_types)
        ideas.append(f"{cat} de {prod}")
    return ideas

if __name__ == "__main__":
    for idx, idea in enumerate(generate_amazon_affiliate_video_ideas(), 1):
        print(f"{idx}. {idea}")
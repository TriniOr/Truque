# src/juegos/truque/ia/facil.py
import random

def calcular_pesos(estado: dict, acciones: list) -> list:
    pesos = []

    for accion, jugador, opciones in acciones:

        if accion == "jugar_carta":
            cartas = estado["jugadores"][jugador]["cartas_en_mano"]
            for idx, carta in cartas.items():
                if carta is not None:
                    pesos.append((accion, jugador, {"carta": idx}, 1.0))

        elif accion in ["apostar_pares", "subir_pares", "apostar_flor", "subir_flor"]:
            min_v = opciones["apuesta"]["min"]
            max_v = opciones["apuesta"]["max"]
            # 70% valor mínimo, 30% aleatorio
            pesos.append((accion, jugador, {"apuesta": min_v}, 0.7))
            pesos.append((accion, jugador, {"apuesta": random.randint(min_v, max_v)}, 0.3))

        else:
            pesos.append((accion, jugador, {}, 1.0))

    return pesos
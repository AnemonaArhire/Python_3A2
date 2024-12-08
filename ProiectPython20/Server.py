import socket
import threading
import random

# Regulile jocului
RULES = {
    "rock": ["scissors", "lizard"],
    "paper": ["rock", "spock"],
    "scissors": ["paper", "lizard"],
    "lizard": ["spock", "paper"],
    "spock": ["scissors", "rock"]
}

MAX_PLAYERS = 3
connected_players = []
lock = threading.Lock()

def determine_result(player_choice, server_choice):
    """
    Determină rezultatul jocului pentru un jucător.
    """
    if player_choice == server_choice:
        return "draw"
    elif server_choice in RULES[player_choice]:
        return "win"
    else:
        return "lose"

def handle_player(player_socket, addr, server_choice):
    """
    Gestionează fiecare jucător conectat.
    """
    print(f"Player {addr} connected.")
    player_socket.sendall(f"Welcome! The server already chose, now it's your turn!".encode())

    try:
        while True:
            player_socket.sendall("Enter your move (rock, paper, scissors, lizard, spock) or type 'exit' to leave: ".encode())
            player_choice = player_socket.recv(1024).decode().strip().lower()

            if player_choice == "exit":
                player_socket.sendall("You chose to exit the game. Goodbye!\n".encode())
                break

            if player_choice not in RULES:
                player_socket.sendall("Invalid move. Try again.\n".encode())
                continue

            print(f"Player {addr} chose: {player_choice}")

            # Determină rezultatul pentru jucător
            result = determine_result(player_choice, server_choice)
            result_message = f"Server chose: {server_choice}. You {result}!\n"

            player_socket.sendall(result_message.encode())

            # Dacă jucătorul pierde, încheiem jocul pentru el
            if result == "lose":
                player_socket.sendall("You lost! Disconnecting...\n".encode())
                break

    except Exception as e:
        print(f"Error with player {addr}: {e}")

    finally:
        player_socket.close()
        with lock:
            connected_players.remove(player_socket)
        print(f"Player {addr} disconnected.")

def main():
    host = "0.0.0.0"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(MAX_PLAYERS)

    print(f"Server started on {host}:{port}. Waiting for players...")

    while True:
        # Așteaptă conexiuni noi
        if len(connected_players) < MAX_PLAYERS:
            client_socket, addr = server_socket.accept()
            with lock:
                connected_players.append(client_socket)

            # Generăm alegerea serverului doar când primul jucător se conectează
            if len(connected_players) == 1:
                server_choice = random.choice(list(RULES.keys()))
                print(f"Server choice for this round: {server_choice}")

            # Lansăm un thread pentru fiecare jucător conectat
            threading.Thread(target=handle_player, args=(client_socket, addr, server_choice)).start()
        elif len(connected_players) > MAX_PLAYERS:
            player_socket.sendall("You cannot enter the game(already at full capacity). Goodbye!\n".encode())

if __name__ == "__main__":
    main()

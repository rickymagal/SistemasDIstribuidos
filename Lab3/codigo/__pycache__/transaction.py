# define a class for transactions
class Transaction:
    # constructor for the class
    def __init__(self, transaction_id: int, challenge: int, solution: str, winner: int) -> None:
        self.transaction_id = transaction_id # Identificador da transação, representada por um valor inteiro;
        self.challenge = challenge # Valor do desafio criptográfico associado à transação, representado por um número [1..6], onde 1 é o desafio mais fácil.
        self.solution = solution # String que, se aplicada a função de hashing SHA-1, solucionará o desafio criptográfico proposto;
        self.winner = winner # ClientID do usuário que solucionou o desafio criptográfico para a referida TransactionID

        


import secrets


class LocalSandboxGateway:
    name="local-sandbox"
    production_ready=False

    def charge(self,token,amount):
        approved=bool(token and token.startswith("tok_approved"))
        return {"status":"approved" if approved else "declined","reference":f"sbx_{secrets.token_hex(10)}","message":"Aprobado por sandbox" if approved else "Rechazado por sandbox"}

    def refund(self,reference,amount):
        return {"status":"approved","reference":f"rf_sbx_{secrets.token_hex(10)}"}

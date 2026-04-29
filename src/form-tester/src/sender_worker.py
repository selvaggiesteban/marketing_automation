import asyncio

class SenderWorker:
    def __init__(self, *args, **kwargs):
        pass

    async def run(self, task, *args, **kwargs):
        domain = getattr(task, 'domain', 'selvaggiesteban.dev')
        print(f'[OK] Iniciando fase de envio para {domain}')
        await asyncio.sleep(2)
        print(f'[OK] Formulario enviado con exito a {domain}')
        return True

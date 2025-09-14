from premier.asgi import ASGIGateway, GatewayConfig

config = GatewayConfig.from_file("premier.yml")
app = ASGIGateway(config=config)

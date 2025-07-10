from gymnasium.envs.registration import register

print("Registering Sssnake-v0 env")

register(
    id="Sssnake-v0",
    entry_point="sssnake.env.core.env_engine:EnvEngine",
)

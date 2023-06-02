import os
import subprocess
from pathlib import Path

root = Path(__file__).parent
env = os.environ.copy()
env["PICCOLO_CONF"] = "db.piccolo_conf"
env["POSTGRES_HOST"] = "localhost"
env["POSTGRES_PORT"] = "5432"
env["POSTGRES_USER"] = "user"
env["POSTGRES_PASSWORD"] = "password123!"
env["POSTGRES_DATABASE"] = "templatecog"
env["PYTHONIOENCODING"] = "utf-8"


def make():
    migration_result = subprocess.run(
        ["piccolo", "migrations", "new", root.name, "--auto"],
        env=env,
        cwd=root,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode()
    print(migration_result)


def run():
    run_result = subprocess.run(
        ["piccolo", "migrations", "forward", root.name],
        env=env,
        cwd=root,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode()
    print(run_result)


if __name__ == "__main__":
    make()
    run()

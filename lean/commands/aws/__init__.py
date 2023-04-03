
from click import group

from lean.commands.aws.s3_push import s3_push

@group()
def aws() -> None:
    # This method is intentionally empty
    # It is used as the command group for all `lean aws <command>` commands
    pass


aws.add_command(s3_push)

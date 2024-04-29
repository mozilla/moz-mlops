import os

from metaflow import (
    FlowSpec, IncludeFile, Parameter,
    card, current, step,
    environment, kubernetes
)
from metaflow.cards import Markdown

from artifact_store import ArtifactStore

GCS_PROJECT_NAME = "project-name-here"
GCS_BUCKET_NAME = "bucket-name-here"

class TemplateFlow(FlowSpec):
    """
    This flow is a template for you to use
    for orchestration of your model.
    """
    example_config = IncludeFile("example_config", default="./example_config.json")

    #This is an example of a parameter. You can toggle this when you call the flow
    # with python template_flow.py run --offline False
    offline_wandb = Parameter(
        "offline",
        help="Do not connect to W&B servers when training",
        type=bool,
        default=True
    )

    # You can uncomment and adjust this decorator when it's time to scale your flow remotely.
    # @kubernetes(image="url-to-docker-image:tag", cpu=1)
    @card(type="default")
    @step
    def start(self):
        """
        Each flow has a 'start' step.

        You can use it for collecting/preprocessing data or other setup tasks.
        """

        self.next(self.train)

    @card
    @environment(vars={
        "WANDB_API_KEY": os.getenv("WANDB_API_KEY"),
        "WANDB_ENTITY": os.getenv("WANDB_ENTITY"),
        "WANDB_PROJECT": os.getenv("WANDB_PROJECT")
    })
    # Note: the image parameter must be a fully qualified registry path otherwise Metaflow will default to
    # the AWS public registry.
    # You can uncomment and adjust this decorator when it's time to scale your flow remotely.
    # @kubernetes(image="url-to-docker-image:tag", gpu=0)
    @step
    def train(self):
        """
        In this step you can train your model,
        save checkpoints and artifacts,
        and deliver data to Weights and Biases
        for experiment evaluation
        """
        import json
        import wandb

        # This can help you fetch and upload artifacts to
        # GCS. Check out help(ArtifactStore) for more details.
        artifact_store = ArtifactStore(
            project_name=GCS_PROJECT_NAME, bucket_name=GCS_BUCKET_NAME
        )

        config_as_dict = json.loads(self.example_config)
        print(f"The config file says: {config_as_dict.get('example_key')}")

        if not self.offline_wandb:
            tracking_run = wandb.init(
                project=os.getenv("WANDB_PROJECT")
            )
            wandb_url = tracking_run.get_url()
            current.card.append(Markdown(f"# WandB training run tracked [here]({wandb_url})"))

        print(f"All set. Running training.")
        # Model training goes here

        self.next(self.end)

    @step
    def end(self):
        """
        This is the mandatory 'end' step: it prints some helpful information
        to access the model and the used dataset.
        """
        print(
            f"""
            Flow complete.

            See artifacts at {GCS_BUCKET_NAME}.
            """
        )


if __name__ == "__main__":
    TemplateFlow()


import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


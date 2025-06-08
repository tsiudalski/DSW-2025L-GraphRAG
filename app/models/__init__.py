"""Init module for models."""

from .templates import Template1, Template2

TEMPLATE_REGISTRY = {
    "template1": Template1,
    "template2": Template2,
}


# TEMPLATE_REGISTRY = Annotated[
#     Union[Template1, Template2],
#     Field(discriminator="template_name")
# ]


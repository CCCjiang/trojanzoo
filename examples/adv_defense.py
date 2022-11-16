#!/usr/bin/env python3

import trojanvision
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    trojanvision.environ.add_argument(parser)
    trojanvision.datasets.add_argument(parser)
    trojanvision.models.add_argument(parser)
    trojanvision.trainer.add_argument(parser)
    trojanvision.attacks.add_argument(parser)
    trojanvision.defenses.add_argument(parser)
    kwargs = parser.parse_args().__dict__

    env = trojanvision.environ.create(**kwargs)
    dataset = trojanvision.datasets.create(**kwargs)
    model = trojanvision.models.create(dataset=dataset, **kwargs)
    trainer = trojanvision.trainer.create(dataset=dataset, model=model, **kwargs)
    attack = trojanvision.attacks.create(dataset=dataset, model=model, **kwargs)
    defense = trojanvision.defenses.create(dataset=dataset, model=model, attack=attack, **kwargs)

    if env['verbose']:
        trojanvision.summary(env=env, dataset=dataset, model=model, trainer=trainer, attack=attack, defense=defense)
    defense.detect(**trainer)

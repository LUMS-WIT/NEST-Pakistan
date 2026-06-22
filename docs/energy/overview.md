# Overview

## Study context

This repository supports the study *Decarbonization Pathways and Equity Implications of Pakistan's Climate Ambition*. The study uses MESSAGEix-Pakistan to explore how Pakistan can meet its climate targets — from the Current Measures baseline through to full Net Zero — while considering distributional and equity implications.

## MESSAGEix-Pakistan

MESSAGEix-Pakistan is a linear energy system optimisation model for Pakistan built on the [`message_ix`](https://docs.messageix.org) and [`ixmp`](https://docs.messageix.org/projects/ixmp) framework maintained by IIASA. It represents Pakistan's energy supply and demand sectors across multiple time periods and optimises least-cost capacity expansion and dispatch subject to policy constraints (emission bounds, renewable targets, reserve margins).

Four scenarios are developed, each solved through the GAMS optimisation solver:

| Scenario | Short name |
|---|---|
| Current Measures | CM |
| NDC-Unconditional | NDC-U |
| NDC-Conditional | NDC-C |
| Net Zero | NZ |


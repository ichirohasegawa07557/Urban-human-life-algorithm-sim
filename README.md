# Urban Human Life Algorithm Simulator

This project is an agent-based urban life simulation.

It models a synthetic city where residents move between:

```text
home -> station -> work/school -> commerce/park/hospital -> home
```

The simulator connects city structure to human daily life:

```text
urban layout
  -> human routine
  -> mobility and congestion
  -> fatigue / satisfaction / spending
  -> energy demand / waste / public service load
  -> city-scale performance
```

## What this project visualizes

- residential districts
- workplaces
- schools
- stations
- commercial areas
- hospitals
- parks
- public administration
- residents as agents
- morning commute
- daytime work/school activity
- lunch / commerce
- evening return
- night recovery
- congestion heatmap
- fatigue and satisfaction
- energy demand and waste
- counterfactual policy effects

## Policy counterfactuals

The project includes examples such as:

- adding a station
- adding a park
- remote work
- mixed-use /職住近接 style city
- hospital-access improvement
- congestion comparison

## Scientific scope

This is not a real urban planning forecast.
It uses synthetic agents and simplified rules.

It is intended as a portfolio-style **urban digital twin / human-life algorithm** showing how:

```text
facility placement + routine + mobility
```

can produce city-level outcomes.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

## Generate simulation

```bash
python scripts/run_urban_life_sim.py
```

## Counterfactual analysis

```bash
python scripts/run_counterfactuals.py
```

## Streamlit app

```bash
streamlit run app.py
```

## Suggested GitHub repository name

```text
urban-human-life-algorithm-sim
```

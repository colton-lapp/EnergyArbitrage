# EnergyArbitrage
Optimizing the arbitrage opportunities of power cost differences with a battery network - final project for 94-867: Decision Analytics for Business and Policy


#### Team Members: Colton Lapp, Justin Poser, Ryan Shen

## Overview:
This repository contains the codebase and report for the final project for Decision Analytics for Business and Policy - 94-867 Fall 2023. Our code webscrapes energy price data from the New York Independent Service Operator (ISO), and then optimizes buying/selling decisions to maximize profits. We formulate our problem as a mixed integer programming problem with a complex array of constriants, and then find the optimal solution using Gurobi/GurobiPy. We also enveloped our code in *Optiguide*, an experimental Natural Language Wrapper developed by Microsoft which utilizes OpenAI's LLMs to translate natural langauge into Gurobi code. Using Optiguide, we translate hypothetical natural langauge requests from our client into executable Python code, and then report how the changes affect the optimal solution.

---

### Read our final report:
Contents:

- Executive Summary
- Mathmematical Formulation
- Optiguide Output

Located at: . . . . . **/FinalReport_EnergyArbitrage.pdf**

---
### Run our code:

We recommend that you run our project through /Code/**example.py**, which calls on the other modules contained within this repo.

To view the results from the Natural Language Wrapper optiguide, view the Jupyter notebook /Code/**energy\_arbitrage\_optiguide.ipynb**

**Webdriver instructions**

To run the webdriver, please ensure that all the python modules have been installed and that you've installed a Selenium webdriver, which is stored in your machine's default package folder.

From there, you'll need to activate your webdriver. Below is a stackoverflow post with instructions for the Chromedriver we use for our project.
https://stackoverflow.com/questions/13724778/how-to-run-selenium-webdriver-test-cases-in-chrome.



### Highlights from Project:

Objective Function Formulation

![alt text](https://github.com/colton-lapp/EnergyArbitrage/blob/main/img/objfunc_stage1.png?raw=true)

Contraints


![alt text](https://github.com/colton-lapp/EnergyArbitrage/blob/main/img/constraints.png?raw=true)

Parameterization

![alt text](https://github.com/colton-lapp/EnergyArbitrage/blob/main/img/parameterization.png?raw=true)

**Results**

Decision Variables: Buy/Sell by type

![alt text](https://github.com/colton-lapp/EnergyArbitrage/blob/main/img/results_buysell.png?raw=true)


Profits over next month

![alt text](https://github.com/colton-lapp/EnergyArbitrage/blob/main/img/results_profits.png?raw=true)
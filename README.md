# Adaptive Behavior Trees
 - code and example
 - see [Hannaford et al., 2016](https://arxiv.org/pdf/1606.09219.pdf)

# Abstract 

Behavior trees (BTs) emerged from video game development as a graphical language for modeling
intelligent agent behavior. However as initially implemented, behavior trees are static plans. This paper adds
to recent literature exploring the ability of BTs to adapt to their success or failure in achieving tasks. The
“Selector” node of a BT tries alternative strategies (its children) and returns success only if all of its children
return failure. This paper studies several means by which Selector nodes can learn from experience, in
particular, learn conditional probabilities of success based on sensor information, and modify the execution
order based on the learned information. Furthermore, a “Greedy Selector” is studied which only tries the child
having the highest success probability. Simulation results indicate significantly increased task performance,
especially when frequentist probability estimate is conditioned on sensor information. The Greedy selector
was ineffective unless it was preceded by a period of training in which all children were exercised.
 
 
To run the demo, as used in the ArXiv paper above, 

```
> python2 bt_icra_sim.py ARG
```
Where ARG is one of ` ['S0', 'S1', 'S2', 'S2g', 'S3', 'S4', 'S5' ]` where 


code | Selector Type
-----|--------------
S0 | Normal "dumb" selector
S1 | Tick in descending order of probability of success
S2 | P(S\|F) condition P(S) on the environment state
S2g | Same as S2 with Greedy selector
S3 | Tick in descending order of cost
S4 | Tick in descending order of utility
S5 | Tick in descending order of utility conditioned on env. state


## based on: 


# BEHAVIOR3PY

This is the official python version of the Behavior3 library, originally written in Javascript.

- Info: https://github.com/behavior3/behavior3py

NOTE: this version still lacks specific documentation, but almost everything you need can be dig from the javascript-version.


## Main features

- Based on the work of [(Marzinotto et al., 2014)](http://www.csc.kth.se/~miccol/Michele_Colledanchise/Publications_files/2013_ICRA_mcko.pdf), in which they propose a **formal**, **consistent** and **general** definition of Behavior Trees;

- **Optimized to control multiple agents**: you can use a single behavior tree instance to handle hundreds of agents;

- It was **designed to load and save trees in a JSON format**, in order to use, edit and test it in multiple environments, tools and languages;

- A **cool visual editor** which you can access online;

- Several **composite, decorator and action nodes** available within the library. You still can define your own nodes, including composites and decorators;

- **Completely free**, the core module and the visual editor are all published under the MIT License, which means that you can use them for your open source and commercial projects;

- **Lightweight**!

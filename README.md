# Adaptive Behavior Trees which learn from experience
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

## ROS (melodic) and Non-ROS
A new demo has been created to illustrate a concrete robot control scenario capable of integration with a real robot arm target (e.g. Raven or dVRK).    
-  To experiment without a ROS/CRTK Installation:  use `abt_move_cp_example.py` and refer to [details](docs/arm_example_for_CRTK.md).
- To experiment WITH a full ROS/CRTK installation, use `crtk_abt_move_cp_example.py`
and follow setup directions in its comments. 

# Acknowledgement: based on: 


# BEHAVIOR3PY

This is the official python version of the Behavior3 library, originally written in Javascript.

- Info: https://github.com/behavior3/behavior3py


## [Wait!  I'm confused about these different BT repositories!](https://github.com/collaborative-robotics/ABT/blob/main/wait_im_confused.md)



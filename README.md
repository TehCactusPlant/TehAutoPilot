# TehAutoPilot <Under Development>
> Current Version: 0.0.1 (unreleased)

### Summary
Application to automate a variety of processes such as desktop UIs, video games and more.

## Concept
### Base designs
[Flowchart for High Level Overview](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/AutoPilot%20HighLevelConcept.png)  
[Flowchart for Database Mapping](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/AutoPilot%20DB%20Plan.png)

### General Breakdown
Application uses Computer Vision / opencv to track simple shapes assembled through thresholding various color ranges. 
These tracked objects are used as reference points for automation logic.

[Image Match with Interference](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/Image$20Match%20With%20Interference.png)  
[Image Match with color many color similarities on screen](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/Image%20Match%20with%20many%20similarities.png)  

[Tkinter UI example](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/AutoPilot%20DB%20Plan.png)
> Developer Note:  
> * Current plan is replacing native tkinter app with a FLASK app/api and a html/js frontend.  
> This is to free up processing resources being used on rendering UI.

Automation process uses a series a Tasks containing a series of steps to be executed. Steps can have positive and 
negative responses that execute other steps and even tasks recursively. 

[Task / Step recursive flow example](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/TaskStep%20Example.png)


For video games a node based navigation system is implemented. Tracking the position of X(example player) moving towards nodes mapped based on image / shape object references.

[Node Plotting Example](https://github.com/TehCactusPlant/TehAutoPilot/tree/main/Concepts/Node%20Navigation%201.png)
> Documentation to be uploaded  on initial version release.
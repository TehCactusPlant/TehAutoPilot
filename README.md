# TehAutoPilot

### Summary
Application to automate a variety of processes such as desktop UIs, video games and more.

### Concept

Application uses Computer Vision / opencv to track simple shapes assembled through thresholding various color ranges. 
These tracked objects are used as reference points for automation logic.

Automation process uses a series a Tasks containing a series of steps to be executed. Steps can have positive and 
negative responses that execute other steps and even tasks recursively. 

For video games a node based navigation system is implemented. Tracking the position of X(example player) moving towards nodes mapped based on image / shape object references.

[Example](https://i.imgur.com/aIhxmRV.png)
> Documentation to be uploaded  on initial version release.
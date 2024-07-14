---
marp: true
---

# a - requirements

## capture and store

- capture videostreams from ip cams (existing infrastructure)

- optional for now: capture video data in other ways 
    - store and forward for higher robustness, ...


--> in any case a server component that can 
    - receive rtsp, ... streams
    - store the received data in a organized and permissioned way
is needed 

- optional for now: increased data security, data lineage, ...  

---

# b - requirements

## image processing

- basic zone    
    - algo / sensitivity adjustable
- different ml/ai models 
    - can be limited to zones
    - could be parameterized


--> zone management 
    - case by case  
    - templates for reproducibility

---

# c - requirements

## automation

- alarms 
    - based on image processing
        - fighting mice
    - based on zones 

- based on system state 
    - missing video data 
    - ...

---

# d - requirements

## view and export 

- for compliance check
- for using the data in  of research

- unclear
    - integrated tag managment needed?
    - managment of externally postprocessed vodeo files 
    - managment of externally generated taging data 
    - managment of externally generated results  

---

# e 1 - status 

## zoneminder ~ ZM

- can capture and store streams
- open source projekt looks not attractive 
    - status of documemtation
    - status of docker 
    - usability
        - handling zones (on a case by case basis) is messy
        - experienced problems with config 
    - has some user/permission system
    - integrating ai/ml models is in early draft stage 
        - on selected images of a stream 
            - in realtime, not for postprocessing

---

# e 2 - status

## zoneminder

- some extension code for imouse exists 
    - who will 
        - develop it further
        - keep it alligned with a further developed zonminder open source


- unclear
    - handling of externally postprocessed streams
    - postprocessing in zoneminder
    - zone templates 
    - zone managment for ai extensions
    - ...

---

# e 3 - status

## frigate ~ FG

- can capture and store streams
    - looks more active in development / attrative 
    - offers a extension model
        - not sure if tis is used for the custom code
    - limited visionai model integration via frigate+ (paid) supported  
    - custom code not working properly 
        - custom code source not available
            - recheck license compatibility 
            - existing custom code seems to integrate badly in frigate  (reupload of video data) 
    - not focused on research data management 

---

# e 4 - status

## frigate

- tbd

---
# f 1 - strategy

## business model

- selling the retrofit hardware is not the business model

- selling a solution for handling research datails is the goal  
    - options in context with open source: 
        - consulting
        - freemium
        - saas
        - (managed) on premise deployment .. full service 
        - premium hardware (data lineage, store&forward, edge processing)
        - premium addon services as alarms ...

---
# f 2 - strategy

## business model 

- more effort needed to become a 
    - data sharing platform
    - data mediator 
    - data broker 
    - ...

--- 

# g 1 - steps forward

## current situation zonminder

- zoneminder 
    - seems to be working better than frigate for now
    - source for extension is available
        - works more OKish the frigate + custom extension
    - author is more responsive (sometimes) 

- use zoneminder but don't invest to much    
---

# g 2 - steps forward

## current situation frigate 

- frigate 
    - source of extension not licensed by imouse
        - effectively imouse is the sales department of the software company 
    - unclear how good frigate and the custom extension can be developed together in the next years
        - already given the current bad integration of postprocessed video files  

- try to get license / function / cooperation issues resolved
- deeper look technical into frigate as basis for development
    - decide go on / no go (more likely)
--- 

# g 3 - steps forward

## questions for the next years 

- moving a open source project (like ZM/FG) into resarch data managment software direction means contributing to the project with unclear results
    - forking is possible: more freedom short term, less shared benefit long term, legacy in code and license 

- how much value is in the limited/not yet working ai/ml integration of the ZM/FG
- how much value is in the limited/badly working zone managment integration of zm/fg


- how limiting are the open source projects ZM/FG for the business model / strategy (tbd)

---

# g 4 - steps forward

## serverside 

- use ZM/FG as is (with so far working extensions / as usable) for data capture and storage

- work on own limited data capture and storage system for data lineage, reliability 
 
- work on own frontend component for management of zones, models, .. for edge deployments and server

- work on own frontend component for management of 
 video data amd metadata 
    - import, export, postprocessing, tagging 

---

# g 5 - steps forward

## hardware / edge 

- look into edge processing for more reliabilty, reduced data size, data lineage, options for premium hardware business model (can be COTS HW with closed software)
    - see: management of edge deployment of zones, models, .. 

---
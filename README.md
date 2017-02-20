# com.castsoftware.uc.springbatch

# Spring Batch Analyzer

# Introduction : 

Spring Batch is an open source framework for batch processing. It is a lightweight, comprehensive solution designed to enable the development of robust batch applications, which are often found in modern enterprise systems. Spring Batch builds upon the POJO-based development approach of the Spring Framework.

This technical package is deliver "as-is". It has been used in a limited number of situations.
This package has been tested in CAST 8.1.x 

## Additional types of objects bring by this extension 
Objects being part of Spring Batch Metamodel : Job, Step, Tasklet, Chunk  

![Spring Batch](/springBatchMetamodel.jpg)

## Cases covered by this extension 

The following cases are covered by the extension : 
- creation of objects for Spring Batch artefacts    
- creation of links from Java class to Spring Batch Jobs 
- creation of links from Spring Batch Jobs to Spring Batch Steps 
- creation of call links from tasklets classes to methods 

## Sample transactions Spring Batch end to end graphical view 
![Sample transaction Spring Batch end to end graphical view](/springBatchCarto.jpg)

## TCC configuration
- classes inheriting from interface org.springframework.batch.core.step.tasklet.Tasklet should be set as Entry Point 
- classes and methods calling org.springframework.batch.item.ItemWriter, org.springframework.batch.item.ItemReader, org.springframework.batch.item.ItemStream, org.springframework.batch.item.ItemStreamReader 
To be included in a next version of the Transaction Configuration Kit 
	

# How to contribute
For bugs, feature requests, and contributions contact Thierry Guégan t.guegan@castsoftware.com.
You may also send a thank you if you find this useful.

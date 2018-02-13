'''
Created on 18 feb 2017

@author: TGU
'''
import cast_upgrades.cast_upgrade_1_5_16 # @UnusedImport
from cast.application import ApplicationLevelExtension, ReferenceFinder, create_link
import logging

class TilesAndSpringWebflowApplication(ApplicationLevelExtension):

    def __init__(self):      
        self.beans = {}
        self.springBatchJob = {}
        self.springBatchStep = {}
        self.target_links = {} 
        
    def end_application(self, application):
        self.global_nb_links = 0 
                
        self.BeansList(application)
        self.SpringBatchJobList(application)
        self.SpringBatchStepList(application)
        self.handle_Steps(application)
        self.Call_to_spring_Batch_Job(application)
        self.Call_from_spring_Batch_Job_to_Step(application)
        self.Call_link_from_tasklet_classes_to_methods(application)
        
        logging.info("Nb of links created globally : " + str(self.global_nb_links)) 
        
    def BeansList(self, application):

        # all classes with a link to a Spring Bean 
        for link in application.links().has_callee(application.objects().is_class()).has_caller(application.objects().has_type('SPRING_BEAN')):
            bean = link.get_caller() 
            bean_name = bean.get_name()
            #logging.debug("Spring Bean [" + bean_name + "]")
            logging.info(" Adding a link call between the bean and the class it rely on") 
            create_link('callLink', bean, link.get_callee())
            if bean_name in self.beans: 
                logging.info(" ---- Warning duplicate on Bean1 [" + bean_name + "]") 
            else: 
                self.beans[bean_name] = bean
        
        for link in application.links().has_callee(application.objects().is_class()).has_caller(application.objects().has_type('JSP_BEAN')):
            bean = link.get_caller() 
            bean_name = bean.get_name()
            #logging.debug("JEE Scoped Bean [" + bean_name + "]")
            logging.info(" Adding a call link between the bean and the class it rely on") 
            create_link('callLink', bean, link.get_callee())            
            if bean_name in self.beans: 
                logging.info(" ---- Warning duplicate on Bean2 [" + bean_name + "]") 
            else: 
                self.beans[bean_name] = bean    
            
        for link in application.links().has_callee(application.objects().is_class()).has_caller(application.objects().has_type('XML_BEAN')):
            bean = link.get_caller() 
            bean_name = bean.get_name()
            #logging.debug("XML Bean [" + bean_name + "]")
            logging.info(" Adding a call link between the bean and the class it rely on") 
            create_link('callLink', bean, link.get_callee())
            if bean_name in self.beans: 
                logging.info(" ---- Warning duplicate on Bean3 [" + bean_name + "]") 
            else: 
                self.beans[bean_name] = bean    
            
    def SpringBatchJobList(self, application):
    
        for springBatchJob in application.objects().has_type('SpringBatchJob'):     
            springBatchJob_name = springBatchJob.get_name()
            #logging.info("Spring Batch Job Name = [" + springBatchJob_name + "]") 
            if springBatchJob_name in self.springBatchJob: 
                logging.info(" ---- Warning duplicate on Spring Batch Job [" + springBatchJob_name + "]") 
            else: 
                self.springBatchJob[springBatchJob_name] = springBatchJob
            
    def SpringBatchStepList(self, application):
    
        for springBatchStep in application.objects().has_type('SpringBatchStep'):     
            springBatchStep_name = str(springBatchStep.get_name())
            #logging.info("Spring Batch Step Name = [" + springBatchStep_name + "]") 
            if springBatchStep_name in self.springBatchStep: 
                logging.info(" ---- Warning duplicate on Spring Batch Step [" + springBatchStep_name + "]") 
            else: 
                self.springBatchStep[springBatchStep_name] = springBatchStep    
    
    def handle_Steps(self, application):
        
        nb_links = 0 
        nb_links2 = 0 
                
        for springBatchStep in application.objects().has_type('SpringBatchStep').load_property('SpringBatchStep.step_tasklet').load_property('SpringBatchStep.step_next').load_property('SpringBatchStep.step_tasklet_chunk').load_property('SpringBatchStep.step_tasklet_transaction_manager'):     
            #logging.info(" Spring Batch Step : [" + str(springBatchStep_name) + "]")
            
            springBatchStep_tasklet = springBatchStep.get_property('SpringBatchStep.step_tasklet')
            #logging.info("== Spring Batch Tasklet = [" + str(springBatchStep_tasklet) + "]") 
            if not springBatchStep_tasklet is None: 
                if springBatchStep_tasklet in self.beans:
                    target_bean = self.beans[str(springBatchStep_tasklet)]
                    #logging.info("== Target bean = [" + str(target_bean) + "]") 
                    create_link('callLink', springBatchStep, target_bean)
                    #logging.debug("Creating link between " + str(springBatchStep) + " and " + str(target_bean))
                    nb_links += 1 
                else: 
                    logging.info(" Tasklet ref : bean not found = [" + str(springBatchStep_tasklet) + "]") 

            springBatchStep_tasklet_transaction_manager = springBatchStep.get_property('SpringBatchStep.step_tasklet_transaction_manager')
            if not springBatchStep_tasklet_transaction_manager is None: 
                logging.info("== Spring Batch Tasklet Transaction-manager= [" + str(springBatchStep_tasklet_transaction_manager) + "]") 
                if springBatchStep_tasklet_transaction_manager in self.beans:
                    target_bean = self.beans[str(springBatchStep_tasklet_transaction_manager)]
                    logging.info("== Target bean = [" + str(target_bean) + "]") 
                    create_link('callLink', springBatchStep, target_bean)
                    logging.debug("Creating link between " + str(springBatchStep) + " and " + str(target_bean))
                    nb_links += 1 
                else: 
                    logging.info(" Tasklet transaction-manager : bean not found = [" + str(springBatchStep_tasklet) + "]") 

            springBatchStep_next = springBatchStep.get_property('SpringBatchStep.step_next') 
            #logging.info("== Spring Batch Next = [" + str(springBatchStep_next) + "]")                          
            if not springBatchStep_next is None: 
                next_split = springBatchStep_next.split('#') 
                for springBatchStep_next_split in next_split: 
                    if springBatchStep_next_split in self.springBatchStep : 
                        target_step = self.springBatchStep[str(springBatchStep_next_split)] 
                        #logging.info("== Target step = [" + str(target_step) + "]")  
                        create_link('callLink', springBatchStep, target_step)
                        #logging.debug("Creating link between " + str(springBatchStep) + " and " + str(target_step))
                        nb_links2 += 1 
                    else: 
                        if springBatchStep_next_split != "": 
                            logging.info(" Next : step not found = [" + str(springBatchStep_next_split) + "]") 
                               
            springBatchStep_chunk = springBatchStep.get_property('SpringBatchStep.step_tasklet_chunk') 
            if not springBatchStep_chunk is None: 
                logging.info("== Spring Batch Next = [" + str(springBatchStep_chunk) + "]")                          
                chunk_split = springBatchStep_chunk.split('#') 
                for springBatchStep_chunk_split in chunk_split:
                    if not springBatchStep_chunk_split == "":  
                        if springBatchStep_chunk_split in self.beans : 
                            target_bean = self.beans[str(springBatchStep_chunk_split)] 
                            logging.info("== Target bean = [" + str(target_bean) + "]")  
                            create_link('callLink', springBatchStep, target_bean)
                            logging.debug("Creating link between " + str(springBatchStep) + " and " + str(target_bean))
                            nb_links += 1 
                        else: 
                            logging.info(" Chunk : bean not found = [" + str(springBatchStep_next_split) + "]") 
                                                           
        logging.debug("Nb of links created between Spring Batch Step and Beans : " + str(nb_links))
        logging.debug("Nb of links created between Spring Batch Step and other Spring Batch Step : " + str(nb_links2))        
        self.global_nb_links += nb_links          
        self.global_nb_links += nb_links2 
                
    def Call_to_spring_Batch_Job(self, application):
        
        springBatch_access = ReferenceFinder()
        springBatch_access.add_pattern("springBatchCall", before="", element="\(Job\)[ ]*context\.getBean\(\"[a-zA-Z0-9_-]+", after="")
        
        nb_links = 0
        
        for o in application.get_files(['JV_FILE']): 

            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
            
            for reference in springBatch_access.find_references_in_file(o):
                #logging.debug("Reference " + reference.value)      
                
                springBatchJob_name = reference.value.split("\"")[1]
                #logging.debug("searching " + springBatchJob_name)
 
                if springBatchJob_name in self.springBatchJob: 
                    springBatchJob_target = self.springBatchJob[springBatchJob_name]
                    create_link('callLink', reference.object, springBatchJob_target, reference.bookmark)
                    logging.debug("Creating link between " + str(reference.object) + " and " + str(springBatchJob_target))
                    nb_links += 1 
                else: 
                    logging.debug("Spring Batch Job not found [" + str(springBatchJob_name) + "]")
                    # Begin Specific for CPP 2017 project 
                    if 'processFlux' in str(springBatchJob_name): 
                        logging.debug(" !!!!!! Spring Batch Job name dynamic ")
                        for springBatchJob_target_processFlux_name in self.springBatchJob: 
                            if 'processFlux' in springBatchJob_target_processFlux_name: 
                                springBatchJob_target_processFlux = self.springBatchJob[springBatchJob_target_processFlux_name]
                                create_link('callLink', reference.object, springBatchJob_target_processFlux, reference.bookmark)
                                logging.debug("Creating link between " + str(reference.object) + " and " + str(springBatchJob_target_processFlux))
                                nb_links += 1   
                    # end Specific for CPP 2017 project 
                  
        logging.debug("Nb of links created between Java classes and Spring Batch Job : " + str(nb_links))
        self.global_nb_links += nb_links              
 
    def Call_from_spring_Batch_Job_to_Step(self, application):
        
        nb_links = 0

        for springBatchStep in application.objects().has_type('SpringBatchStep'):     
            springBatchStep_full_name = springBatchStep.get_fullname()
            #logging.info(" Spring Batch Step name : [" + str(springBatchStep) + "]")
            
            springBatchjob_full_name = springBatchStep_full_name[:-(len(springBatchStep.get_name())+1)]
            springBatchjob_name = springBatchjob_full_name.split('].')[1]
            #logging.info(" Spring Batch Job full name : [" + str(springBatchjob_full_name) + "]")           
            if springBatchjob_name in self.springBatchJob: 
                SpringBatchJob = self.springBatchJob[springBatchjob_name]
                create_link('callLink', SpringBatchJob, springBatchStep)
                logging.debug("Creating link between " + str(SpringBatchJob) + " and " + str(springBatchStep))
                nb_links += 1 
            else: 
                logging.debug("Spring Batch Job not found [" + str(springBatchjob_name) + "]")
            
        logging.debug("Nb of links created between Spring Batch Job  and Spring Batch Step : " + str(nb_links))
        self.global_nb_links += nb_links        
        
        
    def Call_link_from_tasklet_classes_to_methods(self, application):
        
        # Update CSV         
        application.get_knowledge_base().update_cast_system_views()       

        # Update KB job to create links using worktables
        application.update_cast_knowledge_base("Create call links from tasklet classes to methods", """
        delete from CI_LINKS;        
        insert into CI_LINKS (CALLER_ID, CALLED_ID, LINK_TYPE, ERROR_ID)                      
        select tasklet.object_id, tasklet_method.object_id, 'callLink', 0 
         from ctv_links relation, cdt_objects super, cdt_objects tasklet, cdt_objects tasklet_method, ctv_link_types types, csv_objects csv
        where relation.called_id    = super.object_id
          and relation.caller_id = tasklet.object_id 
          and relation.link_type_lo = types.link_type_lo
          and relation.link_type_hi = types.link_type_hi
          and types.link_type_name like 'inherit%'
          and super.object_language_name = 'Java'
          and tasklet.object_type_str = 'Java Class' 
          and super.object_fullname = 'org.springframework.batch.core.step.tasklet.Tasklet'
          and super.object_type_str = 'Java Interface' 
          and csv.object_id = tasklet_method.object_id
          and csv.parent_id = tasklet.object_id
          and tasklet_method.object_type_str = 'Java Method'
          ;
        """)            

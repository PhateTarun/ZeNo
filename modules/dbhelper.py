import sqlite3
import logging

#Logger parameters
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('database.log')
formatter = logging.Formatter('%(levelname)s:%(name)s:%(funcName)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)



class Dbhelper:
 
    def __init__(self):
        try:
            logger.info("Establishing Connection to DB")
            self.conn = sqlite3.connect('students.db')
        except Exception as e:
            logger.error(e)
        else:
            logger.info("DB Connection Established")
    
    def __isRecordExist(self,enroll,table_name):
        c = self.conn.cursor()
        select_query = "SELECT enroll FROM " + table_name + " Where enroll = \"" + enroll + "\"" 
        c.execute(select_query)
        logger.debug(select_query)
        output = c.fetchall()
        logger.debug(output)
        c.close()
        
        if(output == []):
            return False
        else:
            return True

    
    def __getTableName(self,enroll):
        c = self.conn.cursor()

        select_query = "SELECT PROGRAM,SEM FROM USER_SUBJECT WHERE enroll = \"" + enroll + "\""
        
        try:
            c.execute(select_query)
            logger.debug(select_query)
            output = c.fetchall()
            table_name = ''
            for string in output[0]:
                table_name = table_name + string
        except Exception as e:
            logger.error(e)
            return ''
        finally:    
            c.close()
        
        logger.debug(table_name)
        return table_name

    def __updateTotal(self,enroll,table_name):
        c = self.conn.cursor()
        table_name = table_name + "_total"
        select_query = "SELECT * FROM MtechITFirst Where enroll = \"" + enroll + "\""
        delete_query = "DELETE FROM " + table_name + " WHERE enroll = \"" + enroll + "\""
        
        c.execute(select_query)
        marks_list = c.fetchall()

        total_marks =0
        for num in marks_list[0]:
            if(isinstance(num,float) or isinstance(num,int)):
                total_marks = total_marks + num
        
        logger.debug(total_marks)

        if(self.__isRecordExist(enroll,table_name)):
            c.execute(delete_query)
            logger.info(delete_query)
            self.conn.commit()
        
        insert_list = [(enroll),(total_marks)]
        insert_query = "INSERT INTO " + table_name + " Values (?,?)"
        c.execute(insert_query,insert_list)
        logger.info(insert_query)
        self.conn.commit()
        c.close()


    def __set_marks(self,user_details,marks):
        c = self.conn.cursor()
        enroll = user_details["student_id"]
        list_marks = [(enroll),
                    (marks[0]['c1_marks']),(marks[0]['c2_marks']),(marks[0]['c3_marks']),
                    (marks[1]['c1_marks']),(marks[1]['c2_marks']),(marks[1]['c3_marks']),
                    (marks[2]['c1_marks']),(marks[2]['c2_marks']),(marks[2]['c3_marks']),
                    (marks[3]['c1_marks']),(marks[3]['c2_marks']),(marks[3]['c3_marks'])
        ]
        
        table_name = self.__getTableName(enroll)

        delete_query = "DELETE FROM " + table_name + " WHERE enroll = \"" + enroll + "\""
        insert_query = "INSERT INTO " + table_name + " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
        if(self.__isRecordExist(enroll,table_name)):
            c.execute(delete_query)
            self.conn.commit()
        
        c.execute(insert_query,list_marks)
        self.conn.commit()
        c.close()
        self.__updateTotal(enroll,table_name)

    def create_user(self,enroll,mobile,password):
        c = self.conn.cursor()

        delete_query = "DELETE FROM SESSIONS WHERE enroll = \"" + enroll + "\""
        insert_query = "INSERT INTO SESSIONS VALUES (?,?,?)"
        insert_list = [(enroll),(mobile),(password)]

        if(self.__isRecordExist(enroll,"SESSIONS")):
            c.execute(delete_query)
            self.conn.commit()

        c.execute(insert_query,insert_list)
        self.conn.commit() 
        c.close()
    
    
    def register_user(self,user_details,marks):
        c = self.conn.cursor()

        name = user_details["first_name"]
        phone = user_details["phone"]
        enroll = user_details["student_id"]
        program = user_details["program"]
        program = program.replace(' ','')
        program = program.replace('.','')
        sem = user_details["semester"]

        list_users = [(enroll),(name),(phone),('Y')] 
        insert_users = "INSERT INTO USERS VALUES (?,?,?,?)"
        
        
        
        if(self.__isRecordExist(enroll,"users")):
            table_name = "users"
            delete_query = "DELETE FROM " + table_name + " WHERE enroll = \"" + enroll + "\""
            c.execute(delete_query)
            logger.info(delete_query)

        if(self.__isRecordExist(enroll,"user_subject")):
            table_name = "user_subject"
            delete_query = "DELETE FROM " + table_name + " WHERE enroll = \"" + enroll + "\""
            c.execute(delete_query)
            logger.info(delete_query)

        c.execute(insert_users,list_users)
        self.conn.commit()

        list_subject = [(enroll),(program),(sem),
                        (marks[0]['course_id']),
                        (marks[1]['course_id']),
                        (marks[2]['course_id']),
                        (marks[3]['course_id'])]

        insert_subject = "INSERT INTO USER_SUBJECT VALUES (?,?,?,?,?,?,?)"

        c.execute(insert_subject,list_subject)
        self.conn.commit()
        self.__set_marks(user_details,marks)
        c.close()

    def is_registered(self,mobile):
        c = self.conn.cursor()
        select_query = "SELECT enroll FROM SESSIONS Where mobile = \"" + mobile + "\""
        c.execute(select_query)
        output = c.fetchall()
        c.close()
        
        if(output == []):
            return False
        else:
            return True
        
    def get_session(self,mobile):
        c = self.conn.cursor()

        select_query = "SELECT enroll,password FROM SESSIONS Where mobile = \"" + mobile + "\""
        c.execute(select_query)
        result = c.fetchall()
        c.close()
        return [result[0][0], result[0][1]]
        

    def get_analytics(self,enroll):
        c = self.conn.cursor()

        table_name = self.__getTableName(enroll) + "_total"
        
        self_marks_query = "SELECT TOTAL_MARKS FROM " + table_name + " WHERE enroll = \"" + enroll + "\""
        c.execute(self_marks_query)
        self_marks = c.fetchall()
        self_marks = self_marks[0]

        lower_query = "SELECT count(1) from " + table_name + " WHERE enroll in (select enroll from " + table_name + " where total_marks < ? )" 
        c.execute(lower_query,self_marks)
        lower_marks = c.fetchall()

        upper_query = "SELECT count(1) from " + table_name + " WHERE enroll in (select enroll from " + table_name + " where total_marks > ? )" 
        c.execute(upper_query,self_marks)
        upper_marks = c.fetchall()

        equal_query = "SELECT count(1) from " + table_name + " WHERE enroll in (select enroll from " + table_name + " where total_marks = ? )" 
        c.execute(equal_query,self_marks)
        equal_marks = c.fetchall()

        c.close()

        return [lower_marks[0][0] , upper_marks[0][0], equal_marks[0][0]]


    
    def logout(self,mobile):
        c = self.conn.cursor()
        if(self.is_registered(mobile)):
            delete_query = "DELETE FROM SESSIONS Where mobile = \"" + mobile + "\""    
            c.execute(delete_query)
            self.conn.commit()
            c.close()
            return True                
        else:
            return False

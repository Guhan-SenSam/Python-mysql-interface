from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
import shutil
import mysql.connector
import ntpath

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "Guhan",
    database = "test_explorer"
    )

mycursor = mydb.cursor()

mainFormula = "INSERT INTO user_activity (action_id, from_adress, to_adress) VALUES (%s,%s,%s)"

script1 = """SELECT @max := MAX(action_id)+ 1 FROM user_activity; 
PREPARE stmt FROM 'ALTER TABLE user_activity AUTO_INCREMENT = ?';
EXECUTE stmt USING @max;
DEALLOCATE PREPARE stmt;"""

undoFormula = "SELECT * FROM user_activity ORDER BY action_no DESC LIMIT 1"

undoTableFormula = "INSERT INTO undo_activity (action_id, from_adress, to_adress) SELECT action_id, from_adress, to_adress FROM user_activity ORDER BY action_no DESC LIMIT 1;\
                    DELETE FROM user_activity ORDER BY action_no DESC LIMIT 1;"


class root(FloatLayout):
    
    input_path = ObjectProperty()
    
    def copy(self, file_select, input_path):
            print (file_select)
            
    def undo(self):
      mycursor.execute(undoFormula)
      self.undo_data = mycursor.fetchone()
      mycursor.execute(undoTableFormula, multi = "True")
      mydb.commit()
        
class Mainapp(App):
    
    def build(self):
        return root()
    

if __name__ == "__main__":
    Mainapp().run()
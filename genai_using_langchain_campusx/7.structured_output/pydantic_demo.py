from pydantic import BaseModel,Field,EmailStr
from typing import Optional

class Student(BaseModel):
    name:str='SOlana'
    age:Optional[int]=None
    email:EmailStr
    cgpa:float=Field(gt=0 ,lt=1)

new_student = {'name':"Everest",'email':'abc@gmail.com','cgpa':0.3}

student = Student(**new_student)
print(student)
print(new_student)

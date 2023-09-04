#include<Servo.h>

Servo servoVer;

Servo servoHor;

int x;
int y;

int prevX;
int prevY;

const int INPUT_LED = 10;
const int PROCESS_LED = 9;
const int OUTPUT_LED = 8;

void setup()
{
  Serial.begin(9600);

  pinMode(INPUT_LED, OUTPUT);
  pinMode(OUTPUT_LED, OUTPUT);
  pinMode(PROCESS_LED, OUTPUT);

  servoVer.attach(5); //y axisAttach Vertical Servo to Pin 7
  servoHor.attach(4);
  servoVer.write(90);
  servoHor.write(90);
}

void outputting(){
  digitalWrite(OUTPUT_LED, HIGH);
  digitalWrite(INPUT_LED, LOW);
  digitalWrite(PROCESS_LED, LOW);
}

void processing(){
  digitalWrite(OUTPUT_LED, LOW);
  digitalWrite(INPUT_LED, LOW);
  digitalWrite(PROCESS_LED, HIGH);
}

void inputting(){
  digitalWrite(OUTPUT_LED, LOW);
  digitalWrite(INPUT_LED, HIGH);
  digitalWrite(PROCESS_LED, LOW);
}

void Pos()
{
  if(prevX != x || prevY != y)
  {
    int servoX = map(x, 0, 1280, 0, 180);
    int servoY = map(y, 0, 720, 0, 180);

    //servoX = min(servoX, 180);
    //servoX = max(servoX, 70);
    //servoY = min(servoY, 179);
    //servoY = max(servoY, 95);
    
    servoHor.write(servoX);
    servoVer.write(servoY);
  }
}

void loop()
{
  if(Serial.available() > 0)
  {
    if(Serial.read() == '(')  
    {
      x = Serial.parseInt();
      if(Serial.read() == ',')
      {
        y = Serial.parseInt();
       Pos();
      }
    }
    else if (Serial.read() == "process"){
      processing();
    }
    else if (Serial.read() == "output"){
      outputting();
    }
    else if (Serial.read() == "input"){
      inputting();
    }
    else {
      digitalWrite(OUTPUT_LED, LOW);
      digitalWrite(INPUT_LED, LOW);
      digitalWrite(PROCESS_LED, LOW);
    }
  }
  while(Serial.available() > 0){
    Serial.read();
  }
}
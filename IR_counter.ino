const int ir=5;
int counter=0;
int flag = 0;
void setup() {
  // put your setup code here, to run once:
  pinMode(ir, INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.println(digitalRead(ir));

  if(int(digitalRead(ir))==1){
    if (!flag){
      flag = 1;
      counter++;
    }   
  }
  else {
    flag = 0;
  }

  String state = "{";

  state += "\"state\": " + String(int(digitalRead(ir))) + ", ";
  state += "\"count\": " + String(counter) + "}";
  //Serial.print(digitalRead(ir));
  Serial.println(state);
  //delay(100);
}

#define LUZ 13
#define SENS  A0
#define DEF_DELAY 250

int _led_state_ = LOW;
int _horno_state_ = LOW;
int _delay_ = DEF_DELAY;
bool _running_ = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(19200);
  pinMode(LUZ, OUTPUT);
  pinMode(A0, INPUT);
  digitalWrite(LUZ, _led_state_);
}

void loop() {
  // put your main code here, to run repeatedly:
  while(Serial.available()){
    char data = Serial.read();
    switch(data){
      case 'L':
        _led_state_ = HIGH;
        digitalWrite(LUZ, _led_state_);
        break;
      case 'l':
        _led_state_ = LOW;
        digitalWrite(LUZ, _led_state_);
        break;
      case 'H':
        _horno_state_ = HIGH;
        break;
      case 'h':
        _horno_state_ = LOW;
        break;
      case '+':
        _delay_ = _delay_ > 50 ? _delay_- 10 : _delay_;
        break;
      case '-':
        _delay_ = _delay_ < 1000 ? _delay_+ 10 : _delay_;
        break;
      case 'S':
        _running_ = true;
        break;
      case 's':
        _running_ = false;
        break;
    }
  }
  if(_running_){
    Serial.print((float)(millis())/1000.0);
    Serial.print("\t");
    Serial.print(_delay_);
    Serial.print("\t");
    Serial.print(_led_state_ ? "L1\t" : "L0\t");
    Serial.print(_horno_state_ ? "H1\t" : "H0\t");
    Serial.println(analogRead(A0));   
    delay(_delay_);
  }
}

from opendbc.can.parser import CANParser
from opendbc.car import Bus, structs
from opendbc.car.interfaces import CarStateBase
from opendbc.car.body.values import DBC


class CarState(CarStateBase):
  def update(self, can_parsers) -> tuple[structs.CarState, structs.CarStateSP]:
    cp = can_parsers[Bus.main]
    ret = structs.CarState()
    ret_sp = structs.CarStateSP()

    ret.wheelSpeeds.fl = cp.vl['MOTORS_DATA']['SPEED_L']
    ret.wheelSpeeds.fr = cp.vl['MOTORS_DATA']['SPEED_R']

    ret.vEgoRaw = ((ret.wheelSpeeds.fl + ret.wheelSpeeds.fr) / 2.) * self.CP.wheelSpeedFactor

    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = False

    ret.steerFaultPermanent = any([cp.vl['VAR_VALUES']['MOTOR_ERR_L'], cp.vl['VAR_VALUES']['MOTOR_ERR_R'],
                                   cp.vl['VAR_VALUES']['FAULT']])

    ret.charging = cp.vl["BODY_DATA"]["CHARGER_CONNECTED"] == 1
    ret.fuelGauge = cp.vl["BODY_DATA"]["BATT_PERCENTAGE"] / 100

    # irrelevant for non-car
    ret.gearShifter = structs.CarState.GearShifter.drive
    ret.cruiseState.enabled = True
    ret.cruiseState.available = True

    return ret, ret_sp

  @staticmethod
  def get_can_parsers(CP, CP_SP):
    messages = [
      ("MOTORS_DATA", 100),
      ("VAR_VALUES", 10),
      ("BODY_DATA", 1),
    ]
    return {Bus.main: CANParser(DBC[CP.carFingerprint][Bus.main], messages, 0)}

from flask import Flask
 

import collections

collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping


from flask_restplus import Api, Resource, fields
from gpiozero import RGBLED
from time import sleep
from colorzero import Color

#rgbledInstance=None  # physical instance of LED
#rgbledApiModel=None  # API model

app = Flask(__name__)
api = Api(app,
          version='1.0',
          title='RPI REST',
          description='Raspbery Pi RESTful API',
          doc='/docs')

ns = api.namespace('rgbled', description='RGB Led related operations')

led_model = api.model('rgbled', {
    'id': fields.Integer(readonly=True, description='The unique identifier'),
    'red_pin': fields.Integer(readonly=True, description='GPIO for red'),
    'green_pin': fields.Integer(readonly=True, description='GPIO for green'),
    'blue_pin': fields.Integer(readonly=True, description='GPIO for blue'),
    'colour': fields.String(required=True, description='red,or green, blue , black etc')
})



class PinUtil(object):
    def __init__(self):       
        self.counter = 0
        self.led_models = []
 
    def get(self, id):
        for led_model in self.led_models:
            if led_model['id'] == id:
                return led_model
        api.abort(404, f"led {id} doesn't exist.")
 

    def create(self,data):
      
        ledapimodel=   data
        ledapimodel['id']=  self.counter = self.counter + 1
        #ledapimodel['red_pin']= data['red']
        #ledapimodel['green_pin']=   data['green']
        #ledapimodel['blue_pin']=  data['blue']
        self.led_models.append(ledapimodel)

        rgbled = RGBLED(red =  data['red_pin']   , green=  data['green_pin']   , blue= data['red_pin']  )
        rgbled.initial_value=Color('black')     
        
        return  ledapimodel




    def update(self, id, data):
        ledapimodel = self.get(id)
        ledapimodel.update(data)  # this is the dict_object update method
        return  ledapimodel
 


@ns.route('/')  # keep in mind this our ns-namespace (pins/)
class LedList(Resource):
    """Shows a list of all leds , and lets you POST to add new leds"""

    @ns.marshal_list_with(led_model)
    def get(self):
        """List all leds """
        return pin_util.led_models

    @ns.expect(led_model)
    @ns.marshal_with(led_model, code=201)
    def post(self):
        """Create a new pin"""
        return pin_util.create(api.payload)


@ns.route('/<int:id>')
@ns.response(404, 'pin not found')
@ns.param('id', 'The pin identifier')
class Led(Resource):
    """Show a single led item and lets you update/delete them"""

    @ns.marshal_with(led_model)
    def get(self, id):
        """Fetch a led given its resource identifier"""
        return pin_util.get(id)

 

    @ns.expect(led_model, validate=True)
    @ns.marshal_with(led_model)
    def put(self, id):
        """Update a led given its identifier"""
        return pin_util.update(id, api.payload)
    
    @ns.expect(led_model)
    def patch(self, id):
        """Partially update a led given its identifier"""
        return pin_util.update(id, api.payload)

pin_util = PinUtil()
pin_util.create({'red_pin': 12, 'green_pin': 13, 'blue_pin': 19})


if __name__ == '__main__':
    app.run(debug=True)

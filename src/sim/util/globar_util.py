from sim.util.id_gegerator import IdGenerator

_id_gegerator = IdGenerator()

class GlobarUtil:
    
    @staticmethod
    def gen_agent_id():
        return _id_gegerator.gen_agent_id()

    @staticmethod
    def gen_object_id():
        return _id_gegerator.gen_object_id()
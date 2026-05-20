from sim.util.id_generator import IdGenerator

_id_generator = IdGenerator()

class GlobalUtil:
    
    @staticmethod
    def gen_agent_id():
        return _id_generator.gen_agent_id()

    @staticmethod
    def gen_object_id():
        return _id_generator.gen_object_id()
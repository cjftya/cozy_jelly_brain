class ParticipantsDelegate:
    def __init__(self):
        self.available_participants = []

    def get_available_participants(self):
        if not self.available_participants:
            return "주변에 대화할만한 대상이 없음"
            
        return "\n".join([line for line in self.available_participants])

    def add_participant(self, participant):
        self.available_participants.append("- **" + participant + "**")
    
    def remove_participant(self, participant):
        self.available_participants.remove("- **" + participant + "**")

    def clear_participants(self):
        self.available_participants.clear()

    def add_all_participants(self, participants):
        for participant in participants:
            self.add_participant(participant)
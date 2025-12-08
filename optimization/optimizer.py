class Optimizer:

    def compute_optimal_settings(self, predicted_demand):
        settings = []
        for kwh in predicted_demand:
            if kwh > 60:
                settings.append({"HVAC_level": "LOW"})
            elif kwh > 40:
                settings.append({"HVAC_level": "MEDIUM"})
            else:
                settings.append({"HVAC_level": "HIGH"})
        return settings

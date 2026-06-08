from abc import ABC, abstractmethod
from typing import List, Any
from models import ValidationError

class Validator(ABC):
    """Classe de base abstraite pour tous les validateurs."""
    @abstractmethod
    def validate(self, data: dict) -> List[ValidationError]:
        pass

class RequiredFieldsValidator(Validator):
    """Vérifie que les champs obligatoires sont présents et non vides."""
    def __init__(self, fields: List[str]):
        self.fields = fields

    def validate(self, data: dict) -> List[ValidationError]:
        errors = []
        for field in self.fields:
            value = data.get(field)
            # Vérifie si la clé manque ou si la valeur est None ou une chaîne vide
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(ValidationError(
                    field=field,
                    code="MISSING_FIELD",
                    message=f"Le champ '{field}' est obligatoire et ne doit pas être vide."
                ))
        return errors

class RangeValidator(Validator):
    """Vérifie qu'un champ numérique est compris dans un intervalle donné."""
    def __init__(self, field: str, min_val: float, max_val: float):
        self.field = field
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, data: dict) -> List[ValidationError]:
        errors = []
        value = data.get(self.field)
        
        # On ne valide que si la valeur est présente (le RequiredFieldsValidator s'occupe de l'absence)
        if value is not None and value != "None":
            try:
                val_float = float(value)
                if not (self.min_val <= val_float <= self.max_val):
                    errors.append(ValidationError(
                        field=self.field,
                        code="OUT_OF_RANGE",
                        message=f"Valeur {val_float} hors plage [{self.min_val}, {self.max_val}]."
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    field=self.field,
                    code="INVALID_TYPE",
                    message=f"Le champ '{self.field}' doit être un nombre."
                ))
        return errors

class ConsistencyValidator(Validator):
    """Vérifie la cohérence entre le statut de la pompe et le débit d'irrigation."""
    def validate(self, data: dict) -> List[ValidationError]:
        errors = []
        pump_status = data.get("pump_status")
        irrigation = data.get("irrigation_l_min", 0.0)

        # Règle métier : si la pompe est "on", le débit doit être strictement supérieur à 0
        if pump_status == "on":
            try:
                if float(irrigation) <= 0:
                    errors.append(ValidationError(
                        field="irrigation_l_min",
                        code="INCONSISTENT_DATA",
                        message="Débit nul alors que la pompe est activée."
                    ))
            except (ValueError, TypeError):
                pass # Erreur de type gérée par le RangeValidator
        return errors

def run_validators(data: dict, validators: List[Validator]) -> List[ValidationError]:
    """Exécute une séquence de validateurs sur un dictionnaire de données."""
    all_errors = []
    for validator in validators:
        all_errors.extend(validator.validate(data))
    return all_errors
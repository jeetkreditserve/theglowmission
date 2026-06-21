export const PHONE_NUMERIC_MESSAGE = "Phone number can contain digits only.";
export const PHONE_LENGTH_MESSAGE = "Enter a 10-digit phone number.";

export type TypedFieldKind =
  | "text"
  | "textarea"
  | "email"
  | "phone"
  | "select"
  | "checkbox"
  | "radio"
  | "date"
  | "datetime"
  | "number"
  | "json"
  | "jsonList"
  | "image";

export type TypedFieldRule = {
  name: string;
  label: string;
  fieldType: TypedFieldKind;
  required?: boolean;
  validation?: Record<string, unknown>;
  options?: Array<string | number | boolean>;
};

export function stripPhoneDigits(value: string) {
  return value.replace(/\D/g, "");
}

export function phoneInputValue(value: string) {
  const digits = stripPhoneDigits(value);
  return {
    value: digits,
    hadNonDigits: digits !== value
  };
}

export function validateTypedFields(
  fields: TypedFieldRule[],
  getValue: (name: string) => unknown
): Record<string, string> {
  return Object.fromEntries(
    fields
      .map((field) => [field.name, validateTypedField(field, getValue(field.name))] as const)
      .filter(([, error]) => Boolean(error))
  );
}

export function validateTypedField(field: TypedFieldRule, value: unknown): string {
  if (isMissing(field, value)) {
    return "This field is required.";
  }
  if (isBlank(value)) {
    return "";
  }

  const stringValue = String(value).trim();

  if (field.fieldType === "email" && !isValidEmail(stringValue)) {
    return "Enter a valid email address.";
  }

  if (field.fieldType === "phone") {
    if (/\D/.test(stringValue)) {
      return PHONE_NUMERIC_MESSAGE;
    }
    const minLength = validationNumber(field.validation, "min_length");
    const maxLength = validationNumber(field.validation, "max_length");
    if (minLength === undefined && maxLength === undefined && stringValue.length !== 10) {
      return PHONE_LENGTH_MESSAGE;
    }
  }

  if (field.fieldType === "number" && !Number.isFinite(Number(value))) {
    return "Enter a valid number.";
  }

  if ((field.fieldType === "date" || field.fieldType === "datetime") && Number.isNaN(new Date(stringValue).getTime())) {
    return "Enter a valid date.";
  }

  if ((field.fieldType === "select" || field.fieldType === "radio") && field.options?.length) {
    const allowedValues = new Set(field.options.map(String));
    if (!allowedValues.has(stringValue)) {
      return "Select a valid option.";
    }
  }

  const customError = validateCustomRules(field.validation || {}, value);
  if (customError) {
    return customError;
  }

  return "";
}

export function validationNumber(validation: Record<string, unknown> | undefined, key: string) {
  const value = validation?.[key];
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
  }
  return undefined;
}

export function validationString(validation: Record<string, unknown> | undefined, key: string) {
  const value = validation?.[key];
  return typeof value === "string" && value ? value : undefined;
}

function isMissing(field: TypedFieldRule, value: unknown) {
  if (!field.required) return false;
  if (field.fieldType === "checkbox") return value !== true;
  return isBlank(value);
}

function isBlank(value: unknown) {
  return value === null || value === undefined || value === "" || (Array.isArray(value) && value.length === 0);
}

function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function validateCustomRules(validation: Record<string, unknown>, value: unknown) {
  const minLength = validationNumber(validation, "min_length");
  if (minLength !== undefined && String(value).length < minLength) {
    return `Ensure this value has at least ${minLength} characters.`;
  }

  const maxLength = validationNumber(validation, "max_length");
  if (maxLength !== undefined && String(value).length > maxLength) {
    return `Ensure this value has no more than ${maxLength} characters.`;
  }

  const pattern = validationString(validation, "pattern");
  if (pattern) {
    try {
      if (!new RegExp(`^(?:${pattern})$`).test(String(value))) {
        return "Enter a valid value.";
      }
    } catch {
      return "Enter a valid value.";
    }
  }

  const min = validationNumber(validation, "min");
  const max = validationNumber(validation, "max");
  if (min !== undefined || max !== undefined) {
    const numericValue = Number(value);
    if (!Number.isFinite(numericValue)) {
      return "Enter a valid number.";
    }
    if (min !== undefined && numericValue < min) {
      return `Ensure this value is at least ${formatNumber(min)}.`;
    }
    if (max !== undefined && numericValue > max) {
      return `Ensure this value is no more than ${formatNumber(max)}.`;
    }
  }

  return "";
}

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : String(value);
}

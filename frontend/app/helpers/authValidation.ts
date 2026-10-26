export type AuthField = "email" | "password" | "passwordConfirmation";
export type AuthErrors = Partial<Record<AuthField, string>>;

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateEmail(email: string, errors: AuthErrors) {
  const value = email.trim();

  if (!value) {
    errors.email = "Введите электронную почту";
  } else if (!emailPattern.test(value)) {
    errors.email = "Проверьте формат электронной почты";
  }
}

export function validateLoginForm(email: string, password: string): AuthErrors {
  const errors: AuthErrors = {};

  validateEmail(email, errors);
  if (!password) errors.password = "Введите пароль";

  return errors;
}

export function validateRegistrationForm(email: string, password: string, passwordConfirmation: string): AuthErrors {
  const errors: AuthErrors = {};

  validateEmail(email, errors);

  if (!password) {
    errors.password = "Введите пароль";
  } else if (password.length < 8) {
    errors.password = "Пароль должен содержать не менее 8 символов";
  }

  if (!passwordConfirmation) {
    errors.passwordConfirmation = "Повторите пароль";
  } else if (password !== passwordConfirmation) {
    errors.passwordConfirmation = "Пароли не совпадают";
  }

  return errors;
}


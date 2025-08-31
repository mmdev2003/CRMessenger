package validator

import (
	"errors"
	"strings"

	validator "github.com/go-playground/validator/v10"
)

type Validator struct {
	validator *validator.Validate
}

func New() *Validator {
	return &Validator{validator: validator.New()}
}

func (val *Validator) Validate(i interface{}) error {
	err := val.validator.Struct(i)
	if err == nil {
		return nil
	}
	err = errors.New(strings.Replace(err.Error(), "\n", ", ", -1))
	return err
}

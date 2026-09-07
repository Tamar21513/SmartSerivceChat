import React from "react";
import InputField from "./InputField";

// Form fields for entering card payment details
export default function PaymentForm({ paymentData, setPaymentData }) {
  return (
    <div className="payment-form">
      <InputField
        label="Cardholder name"
        type="text"
        value={paymentData.cardOwner}
        placeholder="Full name"
        onChange={(value) =>
          setPaymentData({ ...paymentData, cardOwner: value })
        }
      />

      <InputField
        label="Card number"
        type="text"
        value={paymentData.cardNumber}
        placeholder="0000 0000 0000 0000"
        onChange={(value) =>
          setPaymentData({ ...paymentData, cardNumber: value })
        }
      />

      <div className="payment-row">
        <InputField
          label="Expiry date"
          type="text"
          value={paymentData.expiry}
          placeholder="MM/YY"
          onChange={(value) =>
            setPaymentData({ ...paymentData, expiry: value })
          }
        />

        <InputField
          label="CVV"
          type="password"
          value={paymentData.cvv}
          placeholder="123"
          onChange={(value) =>
            setPaymentData({ ...paymentData, cvv: value })
          }
        />
      </div>
    </div>
  );
}
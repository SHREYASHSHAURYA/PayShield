# PayShield Validation Scenarios

## Scenario 1: Bank impersonation with QR payment pressure

Input:

- Message: I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently.
- Interaction type: text_message
- Payment method: qr_code
- Payment direction: send
  Expected:
- Risk level: critical
- Current stage: payment
- Recommended action: recommend_abort

## Scenario 2: Collect request refund scam

Input:

- Message: Your refund is pending. Approve the collect request to receive your money.
- Interaction type: text_message
- Payment method: collect_request
- Payment direction: receive
  Expected:
- Risk level: high or critical
- Current stage: payment or extraction
- Recommended action: require_extra_confirmation or recommend_abort

## Scenario 3: Remote access fraud setup

Input:

- Message: Install AnyDesk and confirm the payment so I can help complete verification.
- Interaction type: text_message
- Payment method: none
- Payment direction: none
  Expected:
- Risk level: high or critical
- Current stage: extraction
- Recommended action: recommend_abort

## Scenario 4: Legitimate low-risk message

Input:

- Message: Dinner bill split is 500 INR. Send when free.
- Interaction type: text_message
- Payment method: upi_id
- Payment direction: send
  Expected:
- Risk level: low or medium
- Current stage: payment or trust
- Recommended action: safe_to_continue or warn_only

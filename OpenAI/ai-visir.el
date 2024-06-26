(require 'json)
(require 'request)


(defun vizier-send-chat-message (message)
  "Send MESSAGE to OpenAI's GPT-3.5-turbo API and output the response into the active buffer."
  (interactive "sMessage: ")  ; Makes function interactive
  (let ((url "https://api.openai.com/v1/chat/completions")
        (data (json-encode `(("model" . "gpt-3.5-turbo")
                             ("messages" . [((role . "user") (content . ,message))])
                             ("temperature" . 0.7)))))
    (request
     url
     :type "POST"
     :headers `(("Content-Type" . "application/json")
                ("Authorization" . ,(concat "Bearer " gptel-api-key)))
     :data data
     :parser 'json-read
     :success (cl-function
               (lambda (&key data &allow-other-keys)
                 (message "Raw data: %S" data)  ; Debug output
                 (let ((choices (cdr (assoc 'choices data))))
                   (message "Choices: %S" choices)  ; Debug output
                   (if (not (and choices (arrayp choices) (> (length choices) 0)))
                       (message "Unexpected or empty choices field: %S" data)
                     (let* ((first-choice (aref choices 0))
                            (response-message (cdr (assoc 'message first-choice)))
                            (role (cdr (assoc 'role response-message)))
                            (content (cdr (assoc 'content response-message))))
                       ;; Check if both role and content are non-nil
                       (if (and role content)
                           ;; Insert response into the current buffer
                           (save-excursion
                             (goto-char (point-max))
                             (insert (format "\n%s: %s" (capitalize role) content)))
                         (message "Missing role or content in message: %S" response-message)))))))
     :error (cl-function
             (lambda (&key error-thrown &allow-other-keys)
               (message "Error: %S" error-thrown))))))

;; Example usage after modification:
;; M-x vizier-send-chat-message
;; and type your message when prompted.

;;Assistant: Привет! (Privet!)
Assistant: simple, easy, straightforward, basic

(require 'json)
(require 'request)


(defun retrieve-answer (data callback)
  "Process the retrieved DATA and call CALLBACK with the role and content."
  (let* ((choices (cdr (assoc 'choices data)))
         (first-choice (aref choices 0))
         (response-message (cdr (assoc 'message first-choice)))
         (role (cdr (assoc 'role response-message)))
         (content (cdr (assoc 'content response-message))))
    (when (and role content callback)
      (funcall callback role content))))

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
                 (retrieve-answer data (lambda (role content)
                                         (save-excursion
                                           (goto-char (point-max))
                                           (insert (format "\n%s: %s" (capitalize role) content)))))))
     :error (cl-function
             (lambda (&key error-thrown &allow-other-keys)
               (message "Error: %S" error-thrown))))))

(defun vizier-send-region (start end)
  "Send the selected region as a MESSAGE to OpenAI's GPT-3.5-turbo API and replace it with the response."
  (interactive "r")
  (let ((message (buffer-substring-no-properties start end)))
    (vizier-send-chat-message message)
    ))

; Assistant: There are 8 planets in our Solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.
; How many satellites has Jupiter

Assistant: Jupiter has a total of 79 known moons/satellites.

(require 'json)
(require 'request)
(require 'org)

(defun vizier-retrieve-answer (data callback)
  "Process the retrieved DATA and call CALLBACK with the role and content."
  (message "Received data: %S" data)  ;; Debugging: Log the received data
  (let* ((choices (cdr (assoc 'choices data))))
    (if (and choices (arrayp choices))
        (let* ((first-choice (aref choices 0))
               (response-message (cdr (assoc 'message first-choice)))
               (role (cdr (assoc 'role response-message)))
               (content (cdr (assoc 'content response-message))))
          (message "Parsed response: role = %S, content = %S" role content)  ;; Debugging: Log the parsed response
          (when (and role content callback)
            (funcall callback role content)))
      (message "Error: Invalid 'choices' in data: %S" data))))  ;; Debugging: Log an error if 'choices' is invalid

(defun vizier-send-chat-message (message &optional thread-id)
  "Send MESSAGE to OpenAI's GPT-3.5-turbo API and output the response into the active buffer.
If THREAD-ID is provided, the request will be made in the context of that thread."
  (let* ((base-url "https://api.openai.com/v1")
         (url (if thread-id
                  (format "%s/threads/%s/messages" base-url thread-id)
                (format "%s/chat/completions" base-url)))
         (messages `[((role . "user") (content . ,message))])
         (data (if thread-id
                   (json-encode `(("role" . "user")
                                  ("content" . ,message)))
                 (json-encode `(("model" . "gpt-3.5-turbo")
                                ("messages" . ,messages)
                                ("temperature" . 0.7)))))
         (headers (if thread-id
                      `(("Content-Type" . "application/json")
                        ("Authorization" . ,(concat "Bearer " (getenv "OPENAI_API_KEY")))
                        ("OpenAI-Beta" . "assistants=v2"))
                    `(("Content-Type" . "application/json")
                      ("Authorization" . ,(concat "Bearer " (getenv "OPENAI_API_KEY")))))))
    (message "URL: %s" url)
    (message "Data: %s" data)
    (message "Headers: %s" headers)
    (request
     url
     :type "POST"
     :headers headers
     :data data
     :parser 'json-read
     :success (cl-function
               (lambda (&key data &allow-other-keys)
                 (vizier-retrieve-answer data
                                         (lambda (role content)
                                           (save-excursion
                                             (goto-char (point-max))
                                             (insert (format "\n%s: %s" (capitalize role) content)))))))
     :error (cl-function
             (lambda (&key error-thrown &allow-other-keys)
               (message "Error: %S" error-thrown))))))

(defun vizier-org ()
  "Send the content of the current Org header to OpenAI's GPT-3.5-turbo API in the context of vizier-thread-id."
  (interactive)
  (save-excursion
    (org-back-to-heading t)
    (let ((thread-id (org-entry-get nil "vizier-thread-id"))
          (content (org-entry-get nil "ITEM")))
      (if (and thread-id content)
          (vizier-send-chat-message content thread-id)
        (message "vizier-thread-id or content is missing for the current heading")))))

(defun vizier-send-region (start end)
  "Send the selected region as a MESSAGE to OpenAI's GPT-3.5-turbo API and replace it with the response."
  (interactive "r")
  (let ((message (buffer-substring-no-properties start end)))
    (vizier-send-chat-message message)))

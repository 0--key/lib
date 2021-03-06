;;; -*- coding: utf-8-unix -*-
;; This is a symlink from /usr/local/share/emacs/site-lisp/
;; and contains all my macros

;; removes all timing in .srt file
;; usage --> just multiply it by <C-u 1100>

(fset 'srt-remove-timing-data
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ("

 OBOB" 0 "%d")) arg)))

;; move the relatively rare words to a special place
(fset 'separate-rare-words
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ("</p [1;5Aq brare		OD" 0 "%d")) arg)))

;; create a drill item out from ordinary voca-builder item
(fset 'eng-init-drill
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ("OCOCxgoogle-tra	a	o >woOBOBOAOBOBOB[1;3CdrillOBOBOB[1;3C--->" 0 "%d")) arg)))

;; extend the existing drill item with 3 samble paragraphs (requrement)
(fset 'eng-sec-drill
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ("OA  OC w [1;5A[1;5A[1;5Aq xreplace-strin	[][1;5AOA--->drill w[1;5AOA[1;5AOA[1;5A[1;5AOA" 0 "%d")) arg)))


;; create a drill item out from rare word

(defun smart-translate ()
  "Shows the word at current point translation at 
the full screen for several seconds and 
returns to the initial buffer"
  (interactive)
  (google-translate-at-point)
  (switch-to-buffer "*Google Translate*")
  (delete-other-windows)
  (sit-for 9)
  (previous-buffer)
  )

(defun switch-to-buffers-list ()
  "Works as expected"
  (interactive)
  (switch-to-buffer "*Buffer List*")
  (revert-buffer)
  )

(provide 'macro-commands)

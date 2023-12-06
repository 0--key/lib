(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)

(setq calendar-latitude 55.0408104)
   (setq calendar-longitude -7.65058411)
   (setq calendar-location-name "Baile na Bó, Dún na nGall")
;; Set the default mail server and news server as specified by Debian
;; policy.

(setq gnus-nntpserver-file "/etc/news/server")

(setq mail-host-address (let ((name (expand-file-name "/etc/mailname")))
                          (if (not (file-readable-p name))
                              nil
                            (with-temp-buffer
                              (insert-file-contents-literally name)
                              (while (search-forward "\n" nil t)
                                (replace-match "" nil t))
                              (buffer-string)))))

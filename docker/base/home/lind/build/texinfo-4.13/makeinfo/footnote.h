/* footnote.h -- declarations for footnote.c.
   $Id: footnote.h,v 1.5 2007/07/01 21:20:32 karl Exp $

   Copyright (C) 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2007 Free Software
   Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

#ifndef FOOTNOTE_H
#define FOOTNOTE_H

extern int footnote_style_preset;
extern int current_footnote_number;
extern int number_footnotes;
extern int already_outputting_pending_notes;

/* The Texinfo @commands.  */
extern void cm_footnote (void);
extern void cm_footnotestyle (void);

extern int set_footnote_style (char *string);    /* called for -s option */

extern void output_pending_notes (void); /* called for output */

#endif /* !FOOTNOTE_H */

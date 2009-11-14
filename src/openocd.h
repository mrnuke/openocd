/***************************************************************************
 *   Copyright (C) 2005 by Dominic Rath <Dominic.Rath@gmx.de>              *
 *   Copyright (C) 2009 by Zachary T Welch <zw@superlucidity.net>          *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 ***************************************************************************/

#ifndef OPENOCD_H
#define OPENOCD_H

/** 
 * Different applications can define this entry point to override
 * the default openocd main function.  On most systems, this will be
 * defined in src/openocd.c.
 * @param argc normally passed from main()
 * @param argv normally passed from main()
 * @returns return code for main()
 */
int openocd_main(int argc, char *argv[]);

/// used by the server_loop() function in src/server/server.c
void openocd_sleep_prelude(void);
/// used by the server_loop() function in src/server/server.c
void openocd_sleep_postlude(void);

#endif

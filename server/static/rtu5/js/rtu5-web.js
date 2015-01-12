/*
$Id: rtu5-web.js,v 1.2 2014/12/30 02:53:21 dbarndt Exp $
==============================================================================
Copyright (c) LoJack Corporation, 2014 - 
All Rights Reserved.  Unpublished rights reserved under the copyright laws
of the United States.

The software contained on this media is proprietary to and embodies the
confidential technology of LoJack Corporation.  Possession, use,
duplication or dissemination of the software and media is authorized only
pursuant to a valid written license from LoJack Corporation.

EXCEPT AS OTHERWISE EXPRESSLY STATED HERE, THIS SOFTWARE AND RELATED
DOCUMENTATION ARE PROVIDED "AS IS" AND WITHOUT ANY WARRANTY OF ANY KIND
EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  IN NO
EVENT SHALL LoJack Corporation BE LIABLE FOR ANY INDIRECT, SPECIAL,
INCIDENTAL, CONSEQUENTIAL, OR EXEMPLARY DAMAGES (INCLUDING LOSS OF
BUSINESS, LOSS PROFITS, LITIGATION, OR THE LIKE), WHETHER BASED ON BREACH
OF CONTRACT, BREACH OF WARRANTY, TORT (INCLUDING NEGLIGENCE), STRICT
LIABILITY, PRODUCT LIABILITY, OR OTHERWISE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.  THE NEGATION OF DAMAGES SET FORTH ABOVE ARE
FUNDAMENTAL ELEMENTS OF THE BASIS OF THE BARGAIN BETWEEN LoJack Corporation
AND THE USER OF THIS SOFTWARE.  THIS INFORMATION WOULD NOT BE PROVIDED
WITHOUT SUCH LIMITATIONS.  NO INFORMATION, WHETHER ORAL OR WRITTEN,
OBTAINED BY THE USER OF THIS SOFTWARE FROM LoJack Corporation SHALL CREATE
ANY WARRANTY, REPRESENTATION OR GUARANTEE NOT EXPRESSLY STATED IN THIS
TERMS OF SERVICE.  LoJack Corporation DOES NOT REPRESENT OR WARRANT THAT
THIS SOFTWARE WILL BE ERROR-FREE, THAT DEFECTS WILL BE CORRECTED, OR THAT
THIS SOFTWARE IS FREE OF VIRUSES OR OTHER HARMFUL COMPONENTS.  LoJack
Corporation DOES NOT WARRANT OR REPRESENT THAT THE USE OR THE RESULTS OF
THE USE OF THIS SOFTWARE, FROM THIRD PARTIES OR A LINKED SITE WILL BE
CORRECT, ACCURATE, TIMELY, RELIABLE OR OTHERWISE.  UNDER NO CIRCUMSTANCES
WILL LoJack Corporation BE LIABLE FOR ANY LOSS OR DAMAGE CAUSED BY A USER'S
RELIANCE ON INFORMATION OBTAINED THROUGH THIS SOFTWARE, FROM THIRD PARTIES
OR A LINKED SITE, OR USER'S RELIANCE ON ANY PRODUCT OR SERVICE OBTAINED
FROM A THIRD PARTY OR A LINKED SITE.  IT IS THE RESPONSIBILITY OF THE USER
TO EVALUATE THE ACCURACY, COMPLETENESS OR USEFULNESS OF ANY CONTENT
AVAILABLE THROUGH THIS SOFTWARE, FROM A THIRD PARTIES OR OBTAINED FROM A
LINKED SITE.  THE MATERIALS AND CONTENT PROVIDED BY LoJack Corporation
AND ITS PROVIDERS ARE NOT INTENDED TO AND DO NOT CONSTITUTE LEGAL ADVICE.

User modifications to this software may be proposed and submitted to LoJack
Corporation and may be incorporated into this software at the sole
discretion of LoJack Corporation.  User modifications incorporated into
this software shall become the exclusive property of LoJack Corporation.
The user acknowledges that any of their modifications not incorporated into
this software may be superseded or overwritten in future releases.

RESTRICTED RIGHTS LEGEND:  Use, duplication, or disclosure by the U.S.
Government is subject to restrictions as set forth in Subparagraph
(c) (1) (ii) of DFARS 252.227-7013, or in FAR 52.227-19, as applicable.
==============================================================================
*/

RTU5.web = {};
var RTU5W = RTU5.web;

RTU5W._ready = false;
RTU5W._callQ = [];

RTU5W._flushCallQ = function()
{
	while (RTU5W._callQ.length > 0)
	{
		var entry = RTU5W._callQ.shift();

		RTU5W.connection.session.call(
			entry.proc,
			[entry.args]).then(
				function(result)
				{
					entry.cb(result);
				},
				function(err)
				{
					console.log("ERROR:"); console.log(err);
				});
	}
};

RTU5W.call = function(proc, args, cb)
{
	RTU5W._callQ.push({proc: proc, args: args, cb: cb});

	if (RTU5W._ready) { RTU5W._flushCallQ(); }
};

RTU5W.init = function()
{
	function onAuthChallenge(session, method, extra)
	{
		var tickets = {ljop: "ljop", ljadmin: "ljadmin"};

		if (method !== "ticket")
		{
			throw "don't know how to authenticate using '" + method + "'";
		}

		return tickets[RTU5.app.roles.current];
	}

	RTU5W.connection =
		new autobahn.Connection(
			{
				url: "ws://localhost:8080/api",
				realm: RTU5.app.realm,
				authmethods: ["ticket"],
				authid: RTU5.app.roles.current,
				onchallenge: onAuthChallenge
			});

	RTU5W.connection.onopen = function(session, details)
	{
		RTU5W.connection.session = session;

		RTU5W.call(
			"com.lojack.rtu.proc.v1.read",
			{
				uri: "com.lojack.rtu.data.v1.general"
			},
			function(result)
			{
				console.log("back from general read, data:");
				console.log(result);
			});

		RTU5W._ready = true;
		RTU5W._flushCallQ();
	};

	RTU5W.connection.open();
};


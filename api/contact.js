// Vercel serverless function: receives the contact form and emails it via Resend.
//
// Setup (one time, in Vercel → Project → Settings → Environment Variables):
//   RESEND_API_KEY  — from resend.com (free tier is plenty)
//   CONTACT_TO      — optional, defaults to productionbyag@gmail.com
//   CONTACT_FROM    — optional, defaults to "Productions by AG <onboarding@resend.dev>"
//                     (onboarding@resend.dev can only deliver to the email you signed up to
//                      Resend with; verify a domain in Resend to send from your own address)
//
// Without RESEND_API_KEY the endpoint answers 503 and the page offers a
// pre-filled email instead, so no enquiry is lost.

const TO = process.env.CONTACT_TO || 'productionbyag@gmail.com';
const FROM = process.env.CONTACT_FROM || 'Productions by AG <onboarding@resend.dev>';

const clean = (v, max) => String(v == null ? '' : v).replace(/\r/g, '').trim().slice(0, max);

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'method_not_allowed' });
  }

  const isForm = String(req.headers['content-type'] || '').includes('application/x-www-form-urlencoded');
  const reply = (status, payload) => {
    if (isForm) {
      res.setHeader('Location', payload.ok ? '/contact?sent=1' : '/contact?error=1');
      return res.status(303).end();
    }
    return res.status(status).json(payload);
  };

  let b = req.body || {};
  if (typeof b === 'string') {
    try { b = JSON.parse(b); } catch { b = Object.fromEntries(new URLSearchParams(b)); }
  }

  // Honeypot: bots fill the hidden "website" field. Pretend success.
  if (b.website) return reply(200, { ok: true });

  const d = {
    name: clean(b.name, 120),
    email: clean(b.email, 200),
    company: clean(b.company, 160),
    type: clean(b.type, 80),
    timeline: clean(b.timeline, 60),
    message: clean(b.message, 5000),
  };
  if (!d.name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email) || d.message.length < 10) {
    return reply(400, { ok: false, error: 'invalid' });
  }

  const key = process.env.RESEND_API_KEY;
  if (!key) return reply(503, { ok: false, error: 'not_configured' });

  const text = [
    `Name: ${d.name}`,
    `Email: ${d.email}`,
    `Company: ${d.company || '-'}`,
    `Project type: ${d.type || '-'}`,
    `Timeline: ${d.timeline || '-'}`,
    '',
    d.message,
  ].join('\n');

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: FROM,
        to: [TO],
        reply_to: d.email,
        subject: `New enquiry — ${d.type || 'Project'} — ${d.name}`,
        text,
      }),
    });
    if (!r.ok) {
      console.error('Resend error', r.status, await r.text());
      return reply(502, { ok: false, error: 'send_failed' });
    }
    return reply(200, { ok: true });
  } catch (err) {
    console.error('Contact send failed', err);
    return reply(502, { ok: false, error: 'send_failed' });
  }
};

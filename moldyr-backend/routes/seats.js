const express = require('express');
const db = require('../database');
const { requireAuth } = require('../middleware/auth');
const router = express.Router();

// Айтыстың орындарын алу (public)
router.get('/:eventId', (req, res) => {
  const ev = db.getEventById(req.params.eventId);
  if (!ev) return res.status(404).json({ error: 'Айтыс табылмады' });
  const seats = db.getSeatsByEvent(ev.id);
  res.json({ eventId: ev.id, seats });
});

// Бір орын алу
router.get('/single/:id', requireAuth, (req, res) => {
  const seat = db.getSeatById(req.params.id);
  if (!seat) return res.status(404).json({ error: 'Орын табылмады' });
  res.json(seat);
});

// Admin: орын жасау
router.post('/', requireAuth, (req, res) => {
  const { eventId, label, x, y, price } = req.body;
  if (!eventId || !label)
    return res.status(400).json({ error: 'eventId және label міндетті' });
  if (!db.getEventById(eventId))
    return res.status(404).json({ error: 'Айтыс табылмады' });
  const seat = db.createSeat({ eventId, label, x, y, price });
  res.status(201).json(seat);
});

// Admin: орын редакциялау (баға, label)
router.put('/:id', requireAuth, (req, res) => {
  const seat = db.getSeatById(req.params.id);
  if (!seat) return res.status(404).json({ error: 'Орын табылмады' });
  const updated = db.updateSeat(req.params.id, {
    label: req.body.label ?? seat.label,
    x: req.body.x !== undefined ? Number(req.body.x) : seat.x,
    y: req.body.y !== undefined ? Number(req.body.y) : seat.y,
    price: req.body.price !== undefined ? Number(req.body.price) : seat.price,
  });
  res.json(updated);
});

// Admin: орын мәртебесін ауыстыру (free <-> taken)
router.patch('/:id/toggle', requireAuth, (req, res) => {
  const seat = db.toggleSeatStatus(req.params.id);
  if (!seat) return res.status(404).json({ error: 'Орын табылмады' });
  res.json(seat);
});

// Admin: бір орынды жою
router.delete('/:id', requireAuth, (req, res) => {
  if (!db.deleteSeat(req.params.id))
    return res.status(404).json({ error: 'Орын табылмады' });
  res.json({ ok: true });
});

// Admin: айтыстың барлық орындарын жою
router.delete('/event/:eventId', requireAuth, (req, res) => {
  db.deleteSeatsByEvent(req.params.eventId);
  res.json({ ok: true });
});

// Admin: барлық орынды бос немесе алынған ету
router.put('/event/:eventId/bulk', requireAuth, (req, res) => {
  const { status } = req.body;
  if (!['free','taken'].includes(status))
    return res.status(400).json({ error: 'status: free немесе taken' });
  db.bulkSetSeatsStatus(req.params.eventId, status);
  res.json({ ok: true });
});

// Admin: бірнеше орын бір уақытта жасау (batch)
router.post('/batch', requireAuth, (req, res) => {
  const { eventId, seats } = req.body;
  if (!eventId || !Array.isArray(seats))
    return res.status(400).json({ error: 'eventId және seats[] міндетті' });
  if (!db.getEventById(eventId))
    return res.status(404).json({ error: 'Айтыс табылмады' });
  db.deleteSeatsByEvent(eventId);
  const created = seats.map(s => db.createSeat({ eventId, label: s.label, x: s.x, y: s.y, price: s.price }));
  res.status(201).json({ count: created.length, seats: created });
});

module.exports = router;

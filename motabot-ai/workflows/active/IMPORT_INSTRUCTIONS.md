# How to Import v5.300 into n8n

## ⚠️ **Important Note**

Due to n8n AI Agent's complex internal structure, I cannot create a fully working JSON import file. Instead, I've created:

1. ✅ **Complete build guide** - `V5.300_BUILD_GUIDE.md` (step-by-step, copy-paste ready)
2. ✅ **All tool code** - `supabase_query_tools.js` (reference)
3. ✅ **System prompt** - `system_prompt_v5.300.txt`
4. ❌ **JSON import** - Not fully functional (AI Agent needs manual setup)

---

## 🚀 **Recommended Approach: Follow the Build Guide**

**File:** `motabot-ai/workflows/active/V5.300_BUILD_GUIDE.md`

**Time:** ~15 minutes

**Steps:**
1. Create workflow in n8n
2. Add nodes one by one
3. Copy-paste code from guide
4. Connect everything
5. Test!

---

## 🎯 **Why Not Just Import JSON?**

n8n's AI Agent nodes have **internal metadata** that can't be easily replicated:
- Tool definitions with parameter schemas
- AI model connections
- LangChain configuration
- Version-specific formatting

**Manual setup ensures everything works correctly!**

---

## 💡 **Quick Tip**

You can **partially import** the skeleton JSON I created (`MotaBot v5.300 - Database Query Agent.json`), but you'll still need to:
1. Reconfigure the AI Agent node
2. Reconnect the tools
3. Set up the chat model

**It's actually FASTER to just follow the build guide from scratch!**

---

## 📋 **What You Have**

```
motabot-ai/workflows/active/
├── V5.300_BUILD_GUIDE.md                         ← START HERE! ⭐
├── MotaBot v5.300 - Database Query Agent.json    ← Partial skeleton (optional)
└── IMPORT_INSTRUCTIONS.md                        ← This file
```

```
motabot-ai/workflows/code-snippets/
├── supabase_query_tools.js      ← All 4 tool codes (reference)
└── system_prompt_v5.300.txt     ← AI instructions
```

```
motabot-ai/docs/
├── DATABASE_QUERY_AGENT_SETUP.md    ← Detailed explanation
└── V5.300_QUICK_START.md            ← Quick overview
```

---

## ✅ **Recommendation**

**Follow the build guide:**
`motabot-ai/workflows/active/V5.300_BUILD_GUIDE.md`

It's designed for **fast copy-paste** and takes ~15 minutes.

---

**Ready to build it?** Open the guide and let's go! 🚀

